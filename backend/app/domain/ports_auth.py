from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class User:
    id: int
    email: str
    emailpolicy: str
    createdat: datetime


@dataclass(frozen=True)
class OtpRecord:
    id: int
    email: str
    codehash: str
    attempts: int
    maxattempts: int
    expiresat: datetime
    createdat: datetime


class UserRepositoryPort(Protocol):
    async def get_by_email(self, email: str) -> User | None: ...
    async def create(self, email: str) -> User: ...


class OtpRepositoryPort(Protocol):
    async def create(
        self, email: str, codehash: str, expiresat: datetime, maxattempts: int
    ) -> OtpRecord: ...
    async def get_latest_for_email(self, email: str) -> OtpRecord | None: ...
    async def increment_attempts(self, otp_id: int) -> None: ...


class OtpSenderPort(Protocol):
    async def send_code(self, email: str, code: str) -> None: ...


class JwtServicePort(Protocol):
    def issue(self, user_id: int) -> tuple[str, int]: ...
    def verify_and_get_user_id(self, token: str) -> int: ...
