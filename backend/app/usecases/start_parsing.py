"""
Start parsing usecase.
"""

import json
import uuid
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import ParsingRepository, RequestRepository
from app.adapters.parser_client import ParserServiceClient
from app.transport.schemas.moderator_parsing import (
    ParsingRunStatus,
    StartParsingRequestDTO,
    StartParsingResponseDTO,
)


async def start_parsing(
    request_id: int,
    dto: StartParsingRequestDTO,
    session: AsyncSession,
) -> StartParsingResponseDTO:
    """
    Start parsing for a request.
    1. Find request by requestId
    2. Create parsing_request record
    3. For each key, create parsing_run and call parser_service
    4. Return StartParsingResponseDTO
    """
    req_repo = RequestRepository(session)
    parsing_repo = ParsingRepository(session)
    parser_client = ParserServiceClient()

    request_detail = await req_repo.get_detail(request_id)
    if not request_detail:
        raise ValueError(f"Request {request_id} not found")

    keys = request_detail.get("keys", [])
    if not keys:
        raise ValueError(f"Request {request_id} has no keys")

    depth = dto.depth if dto.depth is not None else 10
    depth = max(1, min(10, depth))
    source = dto.source.value if dto.source else "both"

    raw_keys_json = json.dumps([{"id": k["id"], "text": k.get("normalizedtext") or k.get("rawtext")} for k in keys])
    parsing_request = await parsing_repo.create_parsing_request(
        raw_keys_json=raw_keys_json,
        depth=depth,
        source=source,
        comment=f"Parsing for request {request_id}",
    )

    run_id = str(uuid.uuid4())

    for key in keys:
        keyword = key.get("normalizedtext") or key.get("rawtext")
        key_id = key["id"]

        parsing_run = await parsing_repo.create_parsing_run(
            run_id=f"{run_id}-{key_id}",
            request_id=parsing_request.id,
            status=ParsingRunStatus.queued.value,
            depth=depth,
            source=source,
        )

        # Log: run created
        await parsing_repo.create_log(
            run_id=parsing_run.id,
            level="info",
            message=f"Parsing run created for keyword: {keyword}",
            context=json.dumps({"keyword": keyword, "depth": depth, "source": source}),
        )

        try:
            # Log: starting parser service
            await parsing_repo.create_log(
                run_id=parsing_run.id,
                level="info",
                message="Calling parser service",
                context=None,
            )
            
            result = await parser_client.start_parse(
                keyword=keyword,
                depth=depth,
                mode=source,
            )
            parser_task_id = result.get("task_id")
            parsing_run.parser_task_id = parser_task_id
            parsing_run.status = ParsingRunStatus.running.value
            
            # Log: parser service started
            await parsing_repo.create_log(
                run_id=parsing_run.id,
                level="info",
                message="Parser service task started",
                context=json.dumps({"task_id": parser_task_id}),
            )
        except Exception as e:
            parsing_run.status = ParsingRunStatus.failed.value
            parsing_run.error_message = str(e)
            
            # Log: parser service failed
            await parsing_repo.create_log(
                run_id=parsing_run.id,
                level="error",
                message=f"Failed to start parser service: {str(e)}",
                context=None,
            )

    await parsing_repo.commit()

    return StartParsingResponseDTO(
        requestId=request_id,
        runId=run_id,
        status=ParsingRunStatus.running,
    )
