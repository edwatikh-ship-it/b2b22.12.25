from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.ports_auth import JwtServicePort, OtpRepositoryPort, UserRepositoryPort


@dataclass(frozen=True)
class VerifyOtpUseCase:
    otp_repo: OtpRepositoryPort
    user_repo: UserRepositoryPort
    jwt: JwtServicePort

    async def execute(self, email: str, code: str) -> tuple[str, int]:
        rec = await self.otp_repo.get_latest_for_email(email)
        if rec is None:
            raise ValueError("OTP not requested")

        now = datetime.now(UTC)
        if rec.expiresat <= now:
            raise ValueError("OTP expired")

        if rec.attempts >= rec.maxattempts:
            raise ValueError("Too many attempts")

        codehash = hashlib.sha256(code.encode("utf-8")).hexdigest()
        if codehash != rec.codehash:
            await self.otp_repo.increment_attempts(rec.id)
            raise ValueError("Invalid code")

        user = await self.user_repo.get_by_email(email)
        if user is None:
            user = await self.user_repo.create(email=email)

        token, ttl = self.jwt.issue(user_id=user.id)
        return token, ttl
