from dataclasses import dataclass


def _fix_mojibake(s: str) -> str:
    # Если строка выглядит как "Ð..." — это почти всегда UTF-8, ошибочно прочитанный как latin1/cp1252.
    # Пытаемся восстановить. Если не получилось — возвращаем как есть.
    if not s:
        return s
    try:
        if "Ð" in s or "Ñ" in s:
            return s.encode("latin1").decode("utf-8")
    except Exception:
        return s
    return s


@dataclass(frozen=True)
class SupplierSearchItem:
    supplierid: int
    suppliername: str
    inn: str
    website: str | None
    email: str | None
    score: float | None


class SearchSuppliersUseCase:
    def __init__(self, checko_client):
        self._checko = checko_client

    async def execute(self, *, q: str, limit: int) -> list[SupplierSearchItem]:
        q = (q or "").strip()
        if len(q) < 2:
            raise ValueError("q_too_short")

        limit = int(limit)
        if limit <= 0 or limit > 200:
            raise ValueError("invalid_limit")

        raw_items = await self._checko.search_companies(q=q, limit=limit)

        out: list[SupplierSearchItem] = []
        for idx, r in enumerate(raw_items, start=1):
            inn = str(r.get("ИНН") or r.get("inn") or "").strip()

            name_raw = str(r.get("НаимСокр") or r.get("name") or r.get("НаимПолн") or "").strip()
            name = _fix_mojibake(name_raw)

            if not inn or not name:
                continue

            try:
                supplierid = int(inn)
            except Exception:
                supplierid = idx

            contacts = r.get("Контакты") or r.get("contacts") or {}
            emails = contacts.get("Емэйл") or contacts.get("email") or []
            websites = contacts.get("ВебСайт") or contacts.get("website") or None

            email = None
            if isinstance(emails, list) and len(emails) > 0:
                email = _fix_mojibake(str(emails[0]))

            website = _fix_mojibake(str(websites)) if websites else None

            out.append(
                SupplierSearchItem(
                    supplierid=supplierid,
                    suppliername=name,
                    inn=inn,
                    website=website,
                    email=email,
                    score=None,
                )
            )

        return out
