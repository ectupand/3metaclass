from __future__ import annotations

import typing
from hashlib import sha256

from sqlalchemy import select

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def get_by_email(self, email: str) -> Admin | None:
        async with self.app.database.session.begin() as sess:
            q = select(AdminModel).where(AdminModel.email == email)
            result = await sess.execute(q)
            admin = result.scalars().first()
            if admin:
                return admin.to_data()

    async def create_admin(self, email: str, password: str) -> Admin:
        async with self.app.database.session.begin() as sess:
            admin = AdminModel(
                email=email,
                password=sha256(password.encode()).hexdigest())
            sess.add(admin)
            await sess.commit()
            return admin.to_data()
