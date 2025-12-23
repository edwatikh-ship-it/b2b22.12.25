"""
Get parsing results usecase.
"""

import json
import logging
from collections import defaultdict
from datetime import UTC, datetime
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import ParsingRepository
from app.adapters.db.models import ParsingRequestModel
from app.adapters.parser_client import ParserServiceClient
from app.transport.schemas.moderator_parsing import (
    ParsingDomainGroupDTO,
    ParsingResultsByKeyDTO,
    ParsingResultsResponseDTO,
    ParsingRunStatus,
    ParsingSource,
)

logger = logging.getLogger(__name__)


async def get_parsing_results(
    run_id: str,
    session: AsyncSession,
) -> ParsingResultsResponseDTO:
    """
    Get parsing results by runId.
    REAL VERSION: Fetches results from parser service and DB.
    """
    from app.adapters.parser_client import ParserServiceClient
    
    # Get run data from DB
    parsing_repo = ParsingRepository(session)
    run_model = await parsing_repo.get_parsing_run_by_run_id(run_id)
    
    if not run_model:
        raise ValueError(f"No results found for runId {run_id}")
    
    request_id = run_model.request_id
    task_id = run_model.parser_task_id
    
    # If task_id exists, fetch real results from parser service
    if task_id:
        parser_client = ParserServiceClient()
        try:
            parser_result = await parser_client.get_results(task_id)
            status = parser_result.get("status")
            
            if status == "completed":
                # Extract URLs from parser service
                links = parser_result.get("links", [])
                
                # Get blacklisted domains and normalize them (remove www.)
                from app.adapters.db.models import DomainBlacklistDomainModel
                blacklist_stmt = select(DomainBlacklistDomainModel.root_domain)
                blacklist_result = await parsing_repo._session.execute(blacklist_stmt)
                blacklisted_domains_raw = set(blacklist_result.scalars().all())
                # Normalize blacklisted domains (remove www. prefix for matching)
                blacklisted_domains = {domain.replace("www.", "") for domain in blacklisted_domains_raw}
                
                # Get domain decisions (supplier/reseller status)
                from app.adapters.db.models import DomainDecisionModel, ModeratorSupplierModel
                decision_stmt = select(DomainDecisionModel.domain, DomainDecisionModel.status)
                decision_result = await parsing_repo._session.execute(decision_stmt)
                domain_decisions = {row.domain: row.status for row in decision_result.all()}
                
                # Get supplier/reseller domains
                supplier_stmt = select(ModeratorSupplierModel.domain, ModeratorSupplierModel.type).where(
                    ModeratorSupplierModel.domain.isnot(None)
                )
                supplier_result = await parsing_repo._session.execute(supplier_stmt)
                supplier_domains = {row.domain: row.type for row in supplier_result.all() if row.domain}
                
                # Group by domain and filter blacklisted
                groups_by_domain: dict[str, list[str]] = defaultdict(list)
                for link in links:
                    try:
                        parsed = urlparse(link)
                        domain = parsed.netloc or parsed.path.split("/")[0]
                        domain = domain.lower().strip()
                        # Remove www. prefix for matching
                        domain_normalized = domain.replace("www.", "")
                        if domain and domain_normalized not in blacklisted_domains:
                            groups_by_domain[domain].append(link)
                    except:
                        pass
                
                # Create domain groups with status
                # Use actual source from run_model, fallback to yandex if not set
                actual_source = run_model.source or "yandex"
                if actual_source == "google":
                    source_enum = ParsingSource.google
                elif actual_source == "yandex":
                    source_enum = ParsingSource.yandex
                else:  # "both" or unknown
                    source_enum = ParsingSource.yandex  # Default fallback
                
                groups = []
                for domain, urls in groups_by_domain.items():
                    domain_normalized = domain.replace("www.", "")
                    # Check status: first check domain_decisions, then supplier_domains
                    status = None
                    if domain_normalized in domain_decisions:
                        status = domain_decisions[domain_normalized]
                    elif domain_normalized in supplier_domains:
                        status = supplier_domains[domain_normalized]
                    
                    groups.append(
                        ParsingDomainGroupDTO(
                            domain=domain,
                            urls=urls,
                            source=source_enum,
                            title=None,
                            status=status,
                        )
                    )
                
                # Save results to parsing_hits table
                # Get keyword from parsing_request
                parsing_request = await parsing_repo._session.get(ParsingRequestModel, run_model.request_id)
                keywords_json = json.loads(parsing_request.raw_keys_json) if parsing_request.raw_keys_json else []
                keyword = keywords_json[0] if keywords_json else "unknown"
                
                # Save each link as a parsing hit
                for link in links:
                    try:
                        parsed = urlparse(link)
                        domain = parsed.netloc or parsed.path.split("/")[0]
                        domain = domain.lower().strip()
                        if domain:
                            await parsing_repo.create_parsing_hit(
                                run_id=run_model.id,
                                keyword=keyword,
                                url=link,
                                domain=domain,
                                source=actual_source,
                            )
                    except Exception as hit_err:
                        logger.warning(f"Failed to save hit for URL {link}: {hit_err}")
                
                # Update DB with results
                from datetime import datetime, UTC
                await parsing_repo.update_parsing_run_status(
                    run_id=run_id,
                    status="succeeded",
                    finished_at=datetime.now(UTC),
                )
                
                # Create success log entry
                await parsing_repo.create_log(
                    run_id=run_model.id,
                    level="info",
                    message=f"Parsing completed successfully. Found {len(links)} links, saved to database.",
                    context=json.dumps({"links_count": len(links), "domains_count": len(groups_by_domain)})
                )
                
                await parsing_repo.commit()
                
            elif status == "failed":
                from datetime import datetime, UTC
                error_msg = parser_result.get("error", "Unknown error")
                await parsing_repo.update_parsing_run_status(
                    run_id=run_id,
                    status="failed",
                    error_message=error_msg,
                    finished_at=datetime.now(UTC),
                )
                
                # Create error log entry
                await parsing_repo.create_log(
                    run_id=run_model.id,
                    level="error",
                    message=f"Parsing failed: {error_msg}",
                    context=json.dumps({"error": error_msg})
                )
                groups = []
            else:
                # Still running
                groups = []
        except Exception as e:
            # Fallback: try to get results from DB hits
            try:
                # Get blacklisted domains and normalize them (remove www.)
                from app.adapters.db.models import DomainBlacklistDomainModel, DomainDecisionModel, ModeratorSupplierModel
                blacklist_stmt = select(DomainBlacklistDomainModel.root_domain)
                blacklist_result = await parsing_repo._session.execute(blacklist_stmt)
                blacklisted_domains_raw = set(blacklist_result.scalars().all())
                # Normalize blacklisted domains (remove www. prefix for matching)
                blacklisted_domains = {domain.replace("www.", "") for domain in blacklisted_domains_raw}
                
                # Get domain decisions and supplier statuses
                decision_stmt = select(DomainDecisionModel.domain, DomainDecisionModel.status)
                decision_result = await parsing_repo._session.execute(decision_stmt)
                domain_decisions = {row.domain: row.status for row in decision_result.all()}
                
                supplier_stmt = select(ModeratorSupplierModel.domain, ModeratorSupplierModel.type).where(
                    ModeratorSupplierModel.domain.isnot(None)
                )
                supplier_result = await parsing_repo._session.execute(supplier_stmt)
                supplier_domains = {row.domain: row.type for row in supplier_result.all() if row.domain}
                
                hits = await parsing_repo.get_hits_by_run_id(run_model.id)
                groups_by_domain: dict[str, list[str]] = defaultdict(list)
                for hit in hits:
                    domain = hit.domain.lower().strip()
                    domain_normalized = domain.replace("www.", "")
                    if domain and domain_normalized not in blacklisted_domains:
                        groups_by_domain[domain].append(hit.url)
                
                actual_source = run_model.source or "yandex"
                source_enum = ParsingSource.google if actual_source == "google" else ParsingSource.yandex
                
                groups = []
                for domain, urls in groups_by_domain.items():
                    domain_normalized = domain.replace("www.", "")
                    status = None
                    if domain_normalized in domain_decisions:
                        status = domain_decisions[domain_normalized]
                    elif domain_normalized in supplier_domains:
                        status = supplier_domains[domain_normalized]
                    
                    groups.append(
                        ParsingDomainGroupDTO(
                            domain=domain,
                            urls=list(set(urls)),  # Remove duplicates
                            source=source_enum,
                            title=None,
                            status=status,
                        )
                    )
            except:
                groups = []
    else:
        # No task_id, try to get results from DB hits
        # Get blacklisted domains and normalize them (remove www.)
        from app.adapters.db.models import DomainBlacklistDomainModel, DomainDecisionModel, ModeratorSupplierModel
        blacklist_stmt = select(DomainBlacklistDomainModel.root_domain)
        blacklist_result = await parsing_repo._session.execute(blacklist_stmt)
        blacklisted_domains_raw = set(blacklist_result.scalars().all())
        # Normalize blacklisted domains (remove www. prefix for matching)
        blacklisted_domains = {domain.replace("www.", "") for domain in blacklisted_domains_raw}
        
        # Get domain decisions and supplier statuses
        decision_stmt = select(DomainDecisionModel.domain, DomainDecisionModel.status)
        decision_result = await parsing_repo._session.execute(decision_stmt)
        domain_decisions = {row.domain: row.status for row in decision_result.all()}
        
        supplier_stmt = select(ModeratorSupplierModel.domain, ModeratorSupplierModel.type).where(
            ModeratorSupplierModel.domain.isnot(None)
        )
        supplier_result = await parsing_repo._session.execute(supplier_stmt)
        supplier_domains = {row.domain: row.type for row in supplier_result.all() if row.domain}
        
        hits = await parsing_repo.get_hits_by_run_id(run_model.id)
        groups_by_domain: dict[str, list[str]] = defaultdict(list)
        for hit in hits:
            domain = hit.domain.lower().strip()
            domain_normalized = domain.replace("www.", "")
            if domain and domain_normalized not in blacklisted_domains:
                groups_by_domain[domain].append(hit.url)
        
        actual_source = run_model.source or "yandex"
        source_enum = ParsingSource.google if actual_source == "google" else ParsingSource.yandex
        
        groups = []
        for domain, urls in groups_by_domain.items():
            domain_normalized = domain.replace("www.", "")
            status = None
            if domain_normalized in domain_decisions:
                status = domain_decisions[domain_normalized]
            elif domain_normalized in supplier_domains:
                status = supplier_domains[domain_normalized]
            
            groups.append(
                ParsingDomainGroupDTO(
                    domain=domain,
                    urls=list(set(urls)),  # Remove duplicates
                    source=source_enum,
                    title=None,
                    status=status,
                )
            )
    
    # Create results by key (single key with id=1)
    results = [
        ParsingResultsByKeyDTO(
            keyId=1,
            groups=groups,
        )
    ]
    
    return ParsingResultsResponseDTO(
        requestId=request_id,
        runId=run_id,
        results=results,
    )
