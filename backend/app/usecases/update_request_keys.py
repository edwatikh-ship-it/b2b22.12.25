from dataclasses import dataclass

from app.domain.ports import RequestRepositoryPort


@dataclass(frozen=True)
class KeyInput:
    pos: int
    text: str
    qty: float | None = None
    unit: str | None = None


class UpdateRequestKeysUseCase:
    def __init__(self, repo: RequestRepositoryPort) -> None:
        self._repo = repo

    async def execute(self, request_id: int, keys: list[KeyInput]) -> None:
        if not keys:
            raise ValueError("keys must not be empty")

        for k in keys:
            if int(k.pos) < 1:
                raise ValueError("pos must be >= 1")
            if not str(k.text).strip():
                raise ValueError("text must not be empty")

        await self._repo.update_keys(
            request_id=request_id,
            keys=[{"pos": k.pos, "text": k.text, "qty": k.qty, "unit": k.unit} for k in keys],
        )
