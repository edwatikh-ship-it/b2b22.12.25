from __future__ import annotations

import time
from dataclasses import dataclass

import jwt

from app.config import settings


@dataclass(frozen=True)
class JwtService:
    ttl_seconds: int = 3600

    def issue(self, user_id: int) -> tuple[str, int]:
        now = int(time.time())
        exp = now + int(self.ttl_seconds)
        payload = {"sub": int(user_id), "exp": exp, "iat": now}
        token = jwt.encode(payload, settings.JWTSECRET, algorithm="HS256")
        return token, self.ttl_seconds

    def verify_and_get_user_id(self, token: str) -> int:
        payload = jwt.decode(token, settings.JWTSECRET, algorithms=["HS256"])
        sub = payload.get("sub")
        if sub is None:
            raise ValueError("Missing sub")
        return int(sub)
