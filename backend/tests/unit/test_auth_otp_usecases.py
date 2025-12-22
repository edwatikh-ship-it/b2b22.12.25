from datetime import UTC, datetime, timedelta

import pytest

from app.usecases.auth.request_otp import RequestOtpConfig, RequestOtpUseCase
from app.usecases.auth.verify_otp import VerifyOtpUseCase


class FakeOtpRepo:
    def __init__(self):
        self.records = []
        self.attempts = {}

    async def create(self, email: str, codehash: str, expiresat: datetime, maxattempts: int):
        rec = type("Otp", (), {})()
        rec.id = len(self.records) + 1
        rec.email = email
        rec.codehash = codehash
        rec.attempts = 0
        rec.maxattempts = maxattempts
        rec.expiresat = expiresat
        rec.createdat = datetime.now(UTC)
        self.records.append(rec)
        return rec

    async def get_latest_for_email(self, email: str):
        items = [r for r in self.records if r.email == email]
        return items[-1] if items else None

    async def increment_attempts(self, otp_id: int):
        for r in self.records:
            if r.id == otp_id:
                r.attempts += 1
                return


class FakeOtpSender:
    def __init__(self):
        self.sent = []

    async def send_code(self, email: str, code: str) -> None:
        self.sent.append((email, code))


class FakeUserRepo:
    def __init__(self):
        self.users = {}
        self.next_id = 1

    async def get_by_email(self, email: str):
        return self.users.get(email)

    async def create(self, email: str):
        user = type("User", (), {})()
        user.id = self.next_id
        self.next_id += 1
        user.email = email
        user.emailpolicy = "appendonly"
        user.createdat = datetime.now(UTC)
        self.users[email] = user
        return user


class FakeJwt:
    def issue(self, user_id: int):
        return f"token-{int(user_id)}", 3600

    def verify_and_get_user_id(self, token: str) -> int:
        raise NotImplementedError


@pytest.mark.asyncio
async def test_request_otp_generates_6_digits_and_sends():
    otp_repo = FakeOtpRepo()
    sender = FakeOtpSender()
    uc = RequestOtpUseCase(
        otp_repo=otp_repo, otp_sender=sender, cfg=RequestOtpConfig(ttl_minutes=10, max_attempts=5)
    )

    await uc.execute("a@example.com")

    assert len(sender.sent) == 1
    email, code = sender.sent[0]
    assert email == "a@example.com"
    assert len(code) == 6 and code.isdigit()
    assert len(otp_repo.records) == 1
    assert otp_repo.records[0].maxattempts == 5


@pytest.mark.asyncio
async def test_verify_otp_increments_attempts_on_wrong_code():
    otp_repo = FakeOtpRepo()
    sender = FakeOtpSender()
    await RequestOtpUseCase(otp_repo=otp_repo, otp_sender=sender).execute("a@example.com")

    # overwrite expiry to be valid
    otp_repo.records[0].expiresat = datetime.now(UTC) + timedelta(minutes=10)

    uc = VerifyOtpUseCase(otp_repo=otp_repo, user_repo=FakeUserRepo(), jwt=FakeJwt())

    with pytest.raises(ValueError):
        await uc.execute("a@example.com", "000000")

    assert otp_repo.records[0].attempts == 1
