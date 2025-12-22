from dataclasses import dataclass

from app.domain.ports import RequestRepositoryPort


@dataclass(frozen=True)
class KeyInput:
    pos: int
    text: str
    qty: float | None = None
    unit: str | None = None


class CreateRequestManualUseCase:
    def __init__(self, repo: RequestRepositoryPort) -> None:
        self._repo = repo

    async def execute(self, title: str | None, keys: list[KeyInput]) -> int:
        if not keys:
            raise ValueError("keys must not be empty")

        for k in keys:
            if k.pos < 1:
                raise ValueError("pos must be >= 1")
            if not k.text or not k.text.strip():
                raise ValueError("text must not be empty")

        keys_dicts = [{"pos": k.pos, "text": k.text, "qty": k.qty, "unit": k.unit} for k in keys]
        return await self._repo.create_draft(title=title, keys=keys_dicts)
