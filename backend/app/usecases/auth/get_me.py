from __future__ import annotations

from dataclasses import dataclass

from app.domain.ports_auth import User, UserRepositoryPort


@dataclass(frozen=True)
class GetMeUseCase:
    user_repo: UserRepositoryPort

    async def execute(self, user_id: int) -> User:
        raise NotImplementedError("Will be implemented after UserRepositoryPort adds get_by_id")
