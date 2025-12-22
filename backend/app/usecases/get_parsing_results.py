"""
Get parsing results usecase.
"""

import json
from collections import defaultdict
from datetime import UTC, datetime
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import ParsingRepository
from app.adapters.parser_client import ParserServiceClient
from app.transport.schemas.moderator_parsing import (
    ParsingDomainGroupDTO,
    ParsingResultsByKeyDTO,
    ParsingResultsResponseDTO,
    ParsingRunStatus,
    ParsingSource,
)


async def get_parsing_results(
    run_id: str,
    session: AsyncSession,
) -> ParsingResultsResponseDTO:
    """
    Get parsing results by runId.
    1. Find all parsing_runs with run_id prefix (run_id-{key_id})
    2. For each run in "running" status, check parser_service
    3. If completed, save hits to DB
    4. Group results by keyId and domain
    5. Filter out blacklisted domains
    """
    parsing_repo = ParsingRepository(session)
    parser_client = ParserServiceClient()

    runs = await parsing_repo.get_parsing_runs_by_prefix(run_id)

    if not runs:
        raise ValueError(f"No runs found for runId {run_id}")

    request_id = runs[0].request_id if runs else 0

    blacklisted_domains = await parsing_repo.get_blacklisted_domains()

    results_by_key: dict[int, list[dict]] = defaultdict(list)

    for run_obj in runs:
        run_db_id = run_obj.id
        run_full_id = run_obj.run_id
        parser_task_id = run_obj.parser_task_id
        status = run_obj.status

        key_id = int(run_full_id.split("-")[-1]) if "-" in run_full_id else 0

        if status == ParsingRunStatus.running.value and parser_task_id:
            try:
                parser_result = await parser_client.get_results(parser_task_id)
                parser_status = parser_result.get("status")

                if parser_status == "completed":
                    links = parser_result.get("links", [])
                    
                    for link in links:
                        try:
                            parsed = urlparse(link)
                            domain = parsed.netloc or parsed.path.split("/")[0]
                            domain = domain.lower().strip()

                            if domain in blacklisted_domains:
                                continue

                            await parsing_repo.create_parsing_hit(
                                run_id=run_db_id,
                                keyword=run_obj.run_id,
                                url=link,
                                domain=domain,
                                source=run_obj.source or "google",
                                key_id=key_id,
                            )

                            results_by_key[key_id].append({
                                "url": link,
                                "domain": domain,
                                "source": run_obj.source,
                            })
                        except Exception:
                            pass

                    await parsing_repo.update_parsing_run_status(
                        run_id=run_full_id,
                        status=ParsingRunStatus.succeeded.value,
                        finished_at=datetime.now(UTC),
                    )

                elif parser_status == "failed":
                    error_msg = parser_result.get("error", "Unknown error")
                    await parsing_repo.update_parsing_run_status(
                        run_id=run_full_id,
                        status=ParsingRunStatus.failed.value,
                        error_message=error_msg,
                        finished_at=datetime.now(UTC),
                    )

            except Exception as e:
                await parsing_repo.update_parsing_run_status(
                    run_id=run_full_id,
                    status=ParsingRunStatus.failed.value,
                    error_message=str(e),
                    finished_at=datetime.now(UTC),
                )

        elif status in [ParsingRunStatus.succeeded.value, ParsingRunStatus.failed.value]:
            hits = await parsing_repo.get_hits_by_run_id(run_db_id)
            for hit in hits:
                if hit.domain not in blacklisted_domains:
                    results_by_key[key_id].append({
                        "url": hit.url,
                        "domain": hit.domain,
                        "source": hit.source,
                    })

    await parsing_repo.commit()

    results = []
    for key_id, hits in results_by_key.items():
        groups_by_domain: dict[str, list[str]] = defaultdict(list)
        for hit in hits:
            groups_by_domain[hit["domain"]].append(hit["url"])

        groups = [
            ParsingDomainGroupDTO(
                domain=domain,
                urls=urls,
                source=ParsingSource.google if hits[0]["source"] == "google" else ParsingSource.yandex,
            )
            for domain, urls in groups_by_domain.items()
        ]

        results.append(
            ParsingResultsByKeyDTO(
                keyId=key_id,
                groups=groups,
            )
        )

    return ParsingResultsResponseDTO(
        requestId=request_id,
        runId=run_id,
        results=results,
    )
