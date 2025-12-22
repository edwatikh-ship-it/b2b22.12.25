from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(tags=["Auth"])

# In-memory state for tests (persists within process)
_EMAIL_POLICY: str = "appendonly"


class AuthOtpRequestDTO(BaseModel):
    email: EmailStr


class AuthOtpVerifyDTO(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)


class AuthPolicyPutDTO(BaseModel):
    emailpolicy: str


def _require_dev_bearer(authorization: str | None) -> None:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.split(" ", 1)[1].strip()
    if token != "dev":
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/auth/otp/request")
async def auth_otp_request(payload: AuthOtpRequestDTO):
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.post("/auth/otp/verify")
async def auth_otp_verify(payload: AuthOtpVerifyDTO):
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get("/auth/me")
async def auth_me(authorization: str | None = Header(default=None)):
    _require_dev_bearer(authorization)

    return {
        "id": 1,
        "email": "dev@example.com",
        "emailpolicy": _EMAIL_POLICY,
        "createdat": datetime.now(UTC).isoformat(),
    }


@router.put("/auth/policy", include_in_schema=False)
async def auth_policy_put(
    payload: AuthPolicyPutDTO, authorization: str | None = Header(default=None)
):
    global _EMAIL_POLICY
    _require_dev_bearer(authorization)

    if payload.emailpolicy not in ("appendonly", "allowdelete"):
        raise HTTPException(status_code=422, detail="Invalid emailpolicy")

    _EMAIL_POLICY = payload.emailpolicy
    return {"emailpolicy": _EMAIL_POLICY}


@router.get("/auth/oauth/google/start", include_in_schema=False)
async def auth_google_oauth_start():
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get("/auth/oauth/google/callback", include_in_schema=False)
async def auth_google_oauth_callback(code: str):
    raise HTTPException(status_code=501, detail="Not Implemented")
