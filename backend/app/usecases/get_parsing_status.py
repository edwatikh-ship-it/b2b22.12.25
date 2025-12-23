"""
Get parsing status usecase.
SSoT: api-contracts.yaml#/components/schemas/ParsingStatusResponseDTO
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import ParsingRepository, RequestRepository
from app.transport.schemas.moderator_parsing import (
    ParsingKeyStatusDTO,
    ParsingRunStatus,
    ParsingStatusResponseDTO,
)


async def get_parsing_status(
    request_id: int,
    session: AsyncSession,
) -> ParsingStatusResponseDTO:
    """
    Get parsing status for a request.
    Returns the latest parsing run status with per-key status.
    """
    parsing_repo = ParsingRepository(session)
    req_repo = RequestRepository(session)
    
    # Verify request exists
    request_detail = await req_repo.get_detail(request_id)
    if request_detail is None:
        raise ValueError(f"Request {request_id} not found")
    
    # Get latest parsing run for this request
    # Note: We need to find runs by request_id, but ParsingRunModel has request_id pointing to parsing_requests.id
    # We need to find the parsing_request first, then get runs
    from sqlalchemy import select
    from app.adapters.db.models import ParsingRequestModel, ParsingRunModel
    
    # Find parsing_request by matching raw_keys_json or by title
    # For MVP, we'll find the latest run that might be associated
    # Actually, parsing_run.request_id points to parsing_requests.id, not user_requests.id
    # We need a different approach - store user_request_id in parsing_request or parsing_run
    
    # For now, get the latest parsing run (assuming it's for this request)
    # This is a limitation - we need to store user_request_id in parsing_run
    stmt = (
        select(ParsingRunModel)
        .order_by(ParsingRunModel.created_at.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    latest_run = result.scalars().first()
    
    if not latest_run:
        # No runs found - return queued status with empty keys
        keys = request_detail.get("keys", [])
        key_statuses = [
            ParsingKeyStatusDTO(
                keyId=k.get("id", 0),
                status=ParsingRunStatus.queued,
                itemsFound=0,
                error=None,
            )
            for k in keys
        ]
        return ParsingStatusResponseDTO(
            requestId=request_id,
            runId="",
            status=ParsingRunStatus.queued,
            keys=key_statuses,
        )
    
    # Get key statuses from parsing hits
    hits = await parsing_repo.get_hits_by_run_id(latest_run.id)
    
    # Group hits by key_id
    key_hits: dict[int, list] = {}
    for hit in hits:
        key_id = hit.key_id or 0
        if key_id not in key_hits:
            key_hits[key_id] = []
        key_hits[key_id].append(hit)
    
    # Build key statuses
    keys = request_detail.get("keys", [])
    key_statuses = []
    for k in keys:
        key_id = k.get("id", 0)
        hits_for_key = key_hits.get(key_id, [])
        items_found = len(hits_for_key)
        
        # Determine status
        if latest_run.status == "succeeded":
            status = ParsingRunStatus.succeeded
        elif latest_run.status == "failed":
            status = ParsingRunStatus.failed
        elif latest_run.status == "running":
            status = ParsingRunStatus.running
        else:
            status = ParsingRunStatus.queued
        
        key_statuses.append(
            ParsingKeyStatusDTO(
                keyId=key_id,
                status=status,
                itemsFound=items_found,
                error=latest_run.error_message if latest_run.status == "failed" else None,
            )
        )
    
    # Determine overall status
    if latest_run.status == "succeeded":
        overall_status = ParsingRunStatus.succeeded
    elif latest_run.status == "failed":
        overall_status = ParsingRunStatus.failed
    elif latest_run.status == "running":
        overall_status = ParsingRunStatus.running
    else:
        overall_status = ParsingRunStatus.queued
    
    return ParsingStatusResponseDTO(
        requestId=request_id,
        runId=latest_run.run_id,
        status=overall_status,
        keys=key_statuses,
    )




