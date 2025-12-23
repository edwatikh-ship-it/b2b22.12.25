"""
Start parsing usecase.
"""

import json
import uuid
import logging
import asyncio
import httpx

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import ParsingRepository, RequestRepository
from app.adapters.parser_client import ParserServiceClient
from app.adapters.db.session import SessionLocal
from app.transport.schemas.moderator_parsing import (
    ParsingRunStatus,
    StartParsingRequestDTO,
    StartParsingResponseDTO,
)

logger = logging.getLogger(__name__)


async def _update_parsing_status_background(
    run_id: str,
    keyword: str,
    depth: int,
    source: str,
):
    """
    Background coroutine to call parser service and update DB.
    Runs independently after response is sent.
    """
    try:
        logger.info(f"Background: calling parser service for run_id={run_id}")
        
        # Call parser service
        parser_client = ParserServiceClient()
        result = await parser_client.start_parse(
            keyword=keyword,
            depth=depth,
            mode=source,
        )
        
        task_id = result.get("task_id")
        logger.info(f"Background: parser started, task_id={task_id}")
        
        # Update DB with task_id and status=running
        async with SessionLocal() as session:
            parsing_repo = ParsingRepository(session)
            await parsing_repo.update_parsing_run_status(
                run_id=run_id,
                status="running",
                parser_task_id=task_id,
            )
            await parsing_repo.commit()
            logger.info(f"Background: updated run_id={run_id} to running")
            
    except Exception as e:
        logger.error(f"Background task failed for run_id={run_id}: {str(e)}", exc_info=True)
        
        # Update DB with failed status
        try:
            async with SessionLocal() as session:
                parsing_repo = ParsingRepository(session)
                await parsing_repo.update_parsing_run_status(
                    run_id=run_id,
                    status="failed",
                    error_message=str(e),
                )
                await parsing_repo.commit()
        except Exception as db_err:
            logger.error(f"Failed to update failed run in DB: {str(db_err)}")


async def start_parsing(
    request_id: int,
    dto: StartParsingRequestDTO,
    session: AsyncSession,
) -> StartParsingResponseDTO:
    """
    Start parsing for a request.
    
    Architecture:
    1. Create parsing_request and parsing_run in DB
    2. Call parser_service to start parsing (get task_id)
    3. Save task_id and return runId immediately
    4. Parser service continues parsing in background
    """
    logger.info(f"Starting parsing for request_id={request_id}")
    
    # Validate and normalize parameters
    depth = dto.depth if dto.depth is not None else 10
    depth = max(1, min(10, depth))
    source = dto.source.value if dto.source else "both"
    
    # Initialize repositories
    parsing_repo = ParsingRepository(session)
    req_repo = RequestRepository(session)
    
    request_detail = await req_repo.get_detail(request_id)
    if request_detail is None:
        raise ValueError(f"Request {request_id} not found")

    keys = request_detail.get("keys") or []
    keywords = [str(k.get("rawtext") or "").strip() for k in keys]
    keywords = [k for k in keywords if k]
    if not keywords:
        raise ValueError(f"Request {request_id} has no keywords")

    keyword_to_parse = keywords[0]
    
    # Create parsing_request in DB
    parsing_request = await parsing_repo.create_parsing_request(
        raw_keys_json=json.dumps(keywords),
        depth=depth,
        source=source,
        title=f"Parsing for request {request_id}"
    )
    
    # Generate unique run_id
    base_run_id = str(uuid.uuid4())
    
    logger.info(f"Created parsing_request id={parsing_request.id}, run_id={base_run_id}")
    
    # Try to call parser service
    parser_client = ParserServiceClient()
    task_id = None
    parser_status = "queued"
    
    try:
        logger.info(f"Calling parser service: keyword={keyword_to_parse}, depth={depth}, mode={source}")
        result = await parser_client.start_parse(
            keyword=keyword_to_parse,
            depth=depth,
            mode=source,
        )
        task_id = result.get("task_id")
        parser_status = "running"
        logger.info(f"Parser service started successfully: task_id={task_id}")
    except Exception as e:
        logger.error(f"Failed to call parser service: {str(e)}", exc_info=True)
        parser_status = "queued"
    
    # Create parsing_run in DB
    parsing_run = await parsing_repo.create_parsing_run(
        run_id=base_run_id,
        request_id=parsing_request.id,
        parser_task_id=task_id,
        status=parser_status,
        source=source,
        depth=depth,
    )
    
    # Commit to DB
    await parsing_repo.commit()
    
    logger.info(f"Created parsing_run id={parsing_run.id}, status={parser_status}, task_id={task_id}")
    
    # Return with appropriate status
    return StartParsingResponseDTO(
        requestId=request_id,
        runId=base_run_id,
        status=ParsingRunStatus.running if parser_status == "running" else ParsingRunStatus.queued,
    )


async def manual_parsing(
    keyword: str,
    dto: StartParsingRequestDTO,
    session: AsyncSession,
) -> StartParsingResponseDTO:
    """Manual parsing: run parser for a single keyword provided by moderator UI."""
    parsing_repo = ParsingRepository(session)

    keyword = str(keyword).strip()
    if not keyword:
        raise ValueError("keyword is required")

    depth = dto.depth if dto.depth is not None else 10
    depth = max(1, min(10, depth))
    source = dto.source.value if dto.source else "both"

    parsing_request = await parsing_repo.create_parsing_request(
        raw_keys_json=json.dumps([keyword]),
        depth=depth,
        source=source,
        title="Manual parsing",
    )

    run_id = str(uuid.uuid4())
    parser_client = ParserServiceClient()
    task_id = None
    parser_status = "queued"
    error_msg = None

    try:
        logger.info(f"Calling parser service for manual parsing: keyword={keyword}, depth={depth}, mode={source}")
        
        # Skip health check - just try to start parsing directly
        # Health check was causing 503 errors even when service is available
        # The parse endpoint will handle errors gracefully
        
        result = await parser_client.start_parse(
            keyword=keyword,
            depth=depth,
            mode=source,
        )
        task_id = result.get("task_id")
        parser_status = "running"
        logger.info(f"Manual parser started successfully: task_id={task_id}")
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
        # Handle connection/timeout/status errors
        logger.error(f"Parser service connection error: {str(e)}")
        parser_status = "failed"
        error_msg = f"Parser service unavailable. Please start parser service on {parser_client.base_url}"
    except ConnectionError as e:
        logger.error(f"Parser service unavailable: {str(e)}")
        parser_status = "failed"
        error_msg = f"Parser service unavailable. Please start parser service on {parser_client.base_url}"
    except Exception as e:
        logger.error(f"Manual parser call failed: {str(e)}", exc_info=True)
        parser_status = "failed"
        error_msg = str(e)

    from datetime import datetime, UTC
    
    parsing_run = await parsing_repo.create_parsing_run(
        run_id=run_id,
        request_id=parsing_request.id,
        parser_task_id=task_id,
        status=parser_status,
        source=source,
        depth=depth,
    )
    
    # Create initial log entry
    if parser_status == "running":
        await parsing_repo.create_log(
            run_id=parsing_run.id,
            level="info",
            message=f"Parsing started for keyword: {keyword}, depth: {depth}, source: {source}",
            context=json.dumps({"task_id": task_id, "keyword": keyword, "depth": depth, "source": source})
        )
    elif parser_status == "failed" and error_msg:
        await parsing_repo.create_log(
            run_id=parsing_run.id,
            level="error",
            message=f"Parsing failed to start: {error_msg}",
            context=json.dumps({"error": error_msg})
        )
    
    # Store error message if parser failed to start
    if parser_status == "failed" and error_msg:
        await parsing_repo.update_parsing_run_status(
            run_id=run_id,
            status="failed",
            error_message=error_msg,
            finished_at=datetime.now(UTC),
        )
    
    await parsing_repo.commit()

    return StartParsingResponseDTO(
        requestId=0,
        runId=run_id,
        status=ParsingRunStatus.running if parser_status == "running" else (ParsingRunStatus.failed if parser_status == "failed" else ParsingRunStatus.queued),
    )
