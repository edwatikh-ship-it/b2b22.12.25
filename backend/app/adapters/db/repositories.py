import json
from datetime import UTC, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import (
    AttachmentModel,
    DomainBlacklistDomainModel,
    DomainBlacklistUrlModel,
    DomainDecisionModel,
    RequestKeyModel,
    RequestModel,
    RequestRecipientModel,
    UserBlacklistInnModel,
    UserModel,
)
from app.domain.ports import RequestRepositoryPort, UserBlacklistInnRepositoryPort


class RequestRepository(RequestRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_draft(self, title: str | None, keys: list[dict]) -> int:
        req = RequestModel(title=title, filename=None, status="draft")
        self._session.add(req)
        await self._session.flush()

        for k in keys:
            self._session.add(
                RequestKeyModel(
                    request_id=req.id,
                    pos=int(k["pos"]),
                    text=str(k["text"]),
                    qty=k.get("qty"),
                    unit=k.get("unit"),
                )
            )

        await self._session.commit()
        return int(req.id)

    async def list_requests(self, limit: int, offset: int) -> dict:
        total = await self._session.scalar(select(func.count()).select_from(RequestModel))
        rows = await self._session.execute(
            select(RequestModel).order_by(RequestModel.id.desc()).limit(limit).offset(offset)
        )

        items = []
        for r in rows.scalars().all():
            items.append(
                {
                    "id": int(r.id),
                    "filename": r.filename,
                    "status": r.status,
                    "createdat": r.created_at.isoformat()
                    if getattr(r, "created_at", None)
                    else None,
                    "keyscount": 0,
                }
            )

        return {"items": items, "total": int(total or 0)}

    async def get_detail(self, request_id: int) -> dict | None:
        req = await self._session.get(RequestModel, request_id)
        if req is None:
            return None

        rows = await self._session.execute(
            select(RequestKeyModel)
            .where(RequestKeyModel.request_id == request_id)
            .order_by(RequestKeyModel.pos.asc())
        )

        keys = []
        for k in rows.scalars().all():
            keys.append(
                {
                    "id": int(k.id),
                    "pos": int(k.pos),
                    "rawtext": str(k.text),
                    "normalizedtext": str(k.text),
                    "qty": float(k.qty) if k.qty is not None else None,
                    "unit": k.unit,
                    "suppliers": [],
                }
            )

        return {
            "id": int(req.id),
            "filename": req.filename,
            "status": req.status,
            "createdat": req.created_at.isoformat() if getattr(req, "created_at", None) else None,
            "keys": keys,
        }

    async def update_keys(self, request_id: int, keys: list[dict]) -> None:
        # Ensure request exists
        req = await self._session.get(RequestModel, request_id)
        if req is None:
            raise ValueError("not_found")

        # Replace strategy: delete all keys then insert new
        await self._session.execute(
            select(RequestKeyModel.id).where(RequestKeyModel.request_id == request_id)
        )

        await self._session.execute(
            __import__("sqlalchemy")
            .delete(RequestKeyModel)
            .where(RequestKeyModel.request_id == request_id)
        )

        for k in keys:
            self._session.add(
                RequestKeyModel(
                    request_id=req.id,
                    pos=int(k["pos"]),
                    text=str(k["text"]),
                    qty=k.get("qty"),
                    unit=k.get("unit"),
                )
            )

        await self._session.commit()

    async def submit_request(self, request_id: int) -> dict:
        req = await self._session.get(RequestModel, request_id)
        if req is None:
            raise ValueError("not_found")

        # MVP rule: only draft can be submitted
        if str(req.status) != "draft":
            raise ValueError("invalid_state")

        req.status = "confirmed"
        self._session.add(req)
        await self._session.commit()
        return {
            "requestid": int(req.id),
            "newstatus": "confirmed",
            "matchedsuppliers": 0,
            "message": None,
        }

    async def replace_recipients(self, request_id: int, recipients: list[dict]) -> list[dict]:
        # Ensure request exists
        req = await self._session.get(RequestModel, request_id)
        if req is None:
            raise ValueError("not_found")

        # Replace-all: delete all then insert provided list
        await self._session.execute(
            __import__("sqlalchemy")
            .delete(RequestRecipientModel)
            .where(RequestRecipientModel.request_id == request_id)
        )

        for r in recipients:
            self._session.add(
                RequestRecipientModel(
                    request_id=int(request_id),
                    supplier_id=int(r["supplierid"]),
                    selected=bool(r["selected"]),
                )
            )
        await self._session.commit()

        # Return normalized (sorted) for stable API response + tests
        out = [
            {"supplierid": int(r["supplierid"]), "selected": bool(r["selected"])}
            for r in recipients
        ]
        out.sort(key=lambda x: x["supplierid"])
        return out


class AttachmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        title: str | None,
        original_filename: str,
        content_type: str | None,
        size_bytes: int,
        sha256: str | None,
        storage_key: str | None,
    ) -> dict:
        row = AttachmentModel(
            title=title,
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=int(size_bytes),
            sha256=sha256,
            storage_key=storage_key,
            is_deleted=False,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return self._to_dict(row)

    async def list(self, *, limit: int, offset: int) -> dict:
        from sqlalchemy import func, select

        total = await self._session.scalar(
            select(func.count())
            .select_from(AttachmentModel)
            .where(AttachmentModel.is_deleted.is_(False))
        )  # noqa: E712

        rows = (
            (
                await self._session.execute(
                    select(AttachmentModel)
                    .where(AttachmentModel.is_deleted.is_(False))  # noqa: E712
                    .order_by(AttachmentModel.id.desc())
                    .limit(int(limit))
                    .offset(int(offset))
                )
            )
            .scalars()
            .all()
        )

        return {
            "items": [self._to_dict(r) for r in rows],
            "limit": int(limit),
            "offset": int(offset),
            "total": int(total or 0),
        }

    async def get(self, attachment_id: int) -> dict | None:
        row = await self._session.get(AttachmentModel, attachment_id)
        if row is None or row.is_deleted:
            return None
        return self._to_dict(row)

    async def soft_delete(self, attachment_id: int) -> None:
        row = await self._session.get(AttachmentModel, attachment_id)
        if row is None:
            raise ValueError("not_found")
        row.is_deleted = True
        self._session.add(row)
        await self._session.commit()

    def _to_dict(self, row: AttachmentModel) -> dict:
        return {
            "id": int(row.id),
            "title": row.title,
            "originalfilename": row.original_filename,
            "contenttype": row.content_type,
            "sizebytes": int(row.size_bytes),
            "sha256": row.sha256,
            "storagekey": row.storage_key,
            "isdeleted": bool(row.is_deleted),
            "createdat": row.created_at.isoformat() if row.created_at else None,
        }


class UserBlacklistInnRepository(UserBlacklistInnRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_inn(self, user_id: int, inn: str, reason: str | None) -> None:
        exists_stmt = select(UserBlacklistInnModel.id).where(
            UserBlacklistInnModel.user_id == user_id,
            UserBlacklistInnModel.inn == inn,
        )
        existing_id = await self._session.scalar(exists_stmt)
        if existing_id is not None:
            return

        obj = UserBlacklistInnModel(user_id=user_id, inn=inn, reason=reason)
        self._session.add(obj)
        try:
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise

    async def remove_inn(self, user_id: int, inn: str) -> None:
        stmt = delete(UserBlacklistInnModel).where(
            UserBlacklistInnModel.user_id == user_id,
            UserBlacklistInnModel.inn == inn,
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def list_inns(self, user_id: int, limit: int) -> list[dict]:
        stmt = (
            select(UserBlacklistInnModel)
            .where(UserBlacklistInnModel.user_id == user_id)
            .order_by(UserBlacklistInnModel.id.desc())
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        rows = res.scalars().all()
        return [
            {
                "id": r.id,
                "inn": r.inn,
                "supplierid": None,
                "suppliername": None,
                "checkodata": None,
                "reason": r.reason,
                "createdat": r.created_at.isoformat(),
            }
            for r in rows
        ]


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, userid: int, email: str) -> UserModel:
        obj = await self.session.get(UserModel, userid)
        if obj is not None:
            return obj
        obj = UserModel(id=userid, email=email, emailpolicy="appendonly")
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, userid: int) -> UserModel | None:
        return await self.session.get(UserModel, userid)

    async def set_emailpolicy(self, userid: int, emailpolicy: str) -> UserModel:
        obj = await self.get_or_create(userid=userid, email="dev@example.com")
        obj.emailpolicy = emailpolicy
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj


class DomainBlacklistRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_root_domains(self, limit: int) -> list[str]:
        stmt = (
            select(DomainBlacklistDomainModel.root_domain)
            .order_by(DomainBlacklistDomainModel.id.desc())
            .limit(int(limit))
        )
        res = await self._session.execute(stmt)
        return [str(x) for x in res.scalars().all()]

    async def count_domains(self) -> int:
        stmt = select(func.count(DomainBlacklistDomainModel.id))
        total = await self._session.scalar(stmt)
        return int(total or 0)

    async def list_domains(
        self, limit: int, offset: int
    ) -> list[tuple[int, str, object, str | None]]:
        stmt = (
            select(
                DomainBlacklistDomainModel.id,
                DomainBlacklistDomainModel.root_domain,
                DomainBlacklistDomainModel.created_at,
                DomainBlacklistDomainModel.comment,
            )
            .order_by(DomainBlacklistDomainModel.id.desc())
            .limit(int(limit))
            .offset(int(offset))
        )
        res = await self._session.execute(stmt)
        return [(int(i), str(d), ca, c) for (i, d, ca, c) in res.all()]

    async def add_root_domain(self, root_domain: str, comment: str | None = None) -> int:
        root_domain = str(root_domain).strip().lower()
        if not root_domain:
            raise ValueError("empty_domain")

        exists_stmt = select(DomainBlacklistDomainModel).where(
            DomainBlacklistDomainModel.root_domain == root_domain
        )
        existing = (await self._session.execute(exists_stmt)).scalars().first()
        if existing is not None:
            # Variant A: overwrite comment on re-add
            existing.comment = comment
            self._session.add(existing)
            await self._session.commit()
            await self._session.refresh(existing)
            return int(existing.id)

        obj = DomainBlacklistDomainModel(root_domain=root_domain, comment=comment)
        self._session.add(obj)
        try:
            await self._session.commit()
            await self._session.refresh(obj)
            return int(obj.id)
        except Exception:
            await self._session.rollback()
            raise

    async def add_domain_urls(
        self, domain_id: int, urls: list[str], comment: str | None = None
    ) -> None:
        clean = []
        for u in urls or []:
            u = str(u).strip()
            if u:
                clean.append(u)
        if not clean:
            return

        # insert ignore duplicates (best-effort): try add, if unique violation then skip
        for u in clean:
            self._session.add(DomainBlacklistUrlModel(domain_id=domain_id, url=u, comment=comment))
            try:
                await self._session.commit()
            except Exception:
                await self._session.rollback()
                # likely duplicate, ignore
                continue

    async def get_domain_urls(self, domainid: int):
        stmt = (
            select(
                DomainBlacklistUrlModel.url,
                DomainBlacklistUrlModel.comment,
                DomainBlacklistUrlModel.created_at,
            )
            .where(DomainBlacklistUrlModel.domain_id == int(domainid))
            .order_by(DomainBlacklistUrlModel.id.desc())
        )
        res = await self._session.execute(stmt)
        return [(str(u), c, ca) for (u, c, ca) in res.all()]

    async def remove_root_domain(self, root_domain: str) -> None:
        root_domain = str(root_domain).strip().lower()
        stmt = delete(DomainBlacklistDomainModel).where(
            DomainBlacklistDomainModel.root_domain == root_domain
        )
        await self._session.execute(stmt)
        await self._session.commit()


class DomainDecisionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_domain(self, domain: str) -> DomainDecisionModel | None:
        domain = str(domain).strip().lower()
        stmt = select(DomainDecisionModel).where(DomainDecisionModel.domain == domain)
        res = await self._session.execute(stmt)
        return res.scalars().first()

    async def upsert(
        self,
        *,
        domain: str,
        status: str,
        comment: str | None,
        carddata: dict | None,
    ) -> DomainDecisionModel:
        domain = str(domain).strip().lower()

        card_inn = None
        card_name = None
        card_email = None
        card_emails = None
        card_phone = None
        card_comment = None

        if carddata:
            card_inn = carddata.get("inn")
            card_name = carddata.get("name")
            card_email = carddata.get("email")
            emails = carddata.get("emails")
            card_emails = json.dumps(emails) if emails is not None else None
            card_phone = carddata.get("phone")
            card_comment = carddata.get("comment")

        now = datetime.now(tz=UTC)

        stmt = (
            pg_insert(DomainDecisionModel)
            .values(
                domain=domain,
                status=status,
                comment=comment,
                card_inn=card_inn,
                card_name=card_name,
                card_email=card_email,
                card_emails=card_emails,
                card_phone=card_phone,
                card_comment=card_comment,
                created_at=now,
                updated_at=now,
            )
            .on_conflict_do_update(
                index_elements=[DomainDecisionModel.domain],
                set_={
                    "status": status,
                    "comment": comment,
                    "card_inn": card_inn,
                    "card_name": card_name,
                    "card_email": card_email,
                    "card_emails": card_emails,
                    "card_phone": card_phone,
                    "card_comment": card_comment,
                    "updated_at": now,
                },
            )
            .returning(DomainDecisionModel)
        )

        row = (await self._session.execute(stmt)).scalars().first()
        await self._session.commit()
        return row

    async def delete_by_domain(self, domain: str) -> None:
        domain = str(domain).strip().lower()
        obj = await self.get_by_domain(domain)
        if obj is None:
            return
        await self._session.delete(obj)
        await self._session.commit()
