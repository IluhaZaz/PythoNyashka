from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.infrastructure.storage.postgresql.models import User


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def register(self, email: str, pass_hash: str, profile_id: str) -> str:
        user = User(
            email=email,
            password_hash=pass_hash,
            profile_id=profile_id
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.commit()

        return user.id
