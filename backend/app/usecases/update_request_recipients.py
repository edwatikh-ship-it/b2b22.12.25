from dataclasses import dataclass

from app.domain.ports import RequestRepositoryPort


@dataclass(frozen=True)
class RecipientInput:
    supplierid: int
    selected: bool


class UpdateRequestRecipientsUseCase:
    def __init__(self, repo: RequestRepositoryPort):
        self._repo = repo

    async def execute(self, *, request_id: int, recipients: list[RecipientInput]) -> list[dict]:
        if request_id <= 0:
            raise ValueError("invalid_request_id")

        if recipients is None:
            raise ValueError("invalid_recipients")

        # replace-all допускает полный список, включая selected=false
        for r in recipients:
            if int(r.supplierid) <= 0:
                raise ValueError("invalid_supplierid")

        # repo returns normalized list[dict]: {"supplierid": int, "selected": bool}
        return await self._repo.replace_recipients(
            request_id=request_id,
            recipients=[
                {"supplierid": int(r.supplierid), "selected": bool(r.selected)} for r in recipients
            ],
        )
