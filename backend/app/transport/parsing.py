"""Parsing transport layer (parserservice client + blacklist filter).
SSoT: api-contracts.yaml parsing DTOs.
"""

import urllib.parse

from publicsuffix2 import get_sld

from app.adapters.db.repositories import DomainBlacklistRepository
from app.transport.schemas.moderator_parsing import ParsingDomainGroupDTO


async def parse_query(query: str, depth: int = 1, session=None) -> list[ParsingDomainGroupDTO]:
    """Parse query → URLs → blacklist filter → domain groups.
    MVP: mock URLs (parserservice Playwright 500).
    """
    # Mock URLs (parserservice down)
    mock_urls = [
        f"https://{query.replace(' ', '').lower()}.ru",
        "https://metall.ru",
        "https://stal.ru",
        "https://supplier.ru",
    ]

    # Fetch blacklist
    blacklist = set()
    if session:
        repo = DomainBlacklistRepository(session)
        items = await repo.list_root_domains(limit=1000)
        blacklist = {str(x).strip().lower() for x in items}

    # Filter + group
    grouped = {}
    for url in mock_urls:
        domain = urllib.parse.urlparse(url).netloc
        if not domain:
            continue
        root = get_sld(domain) or domain.lower()
        if root in blacklist:
            continue
        grouped.setdefault(root, []).append(url)

    # DTOs
    return [
        ParsingDomainGroupDTO(domain=d, urls=u, source=None, title=None) for d, u in grouped.items()
    ]
