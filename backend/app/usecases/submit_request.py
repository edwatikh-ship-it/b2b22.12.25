from app.domain.ports import RequestRepositoryPort


class SubmitRequestUseCase:
    def __init__(self, repo: RequestRepositoryPort) -> None:
        self._repo = repo

    async def execute(self, request_id: int) -> dict:
        return await self._repo.submit_request(request_id=request_id)
