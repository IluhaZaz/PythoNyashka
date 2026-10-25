from datetime import datetime

from sqlalchemy import select
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.infrastructure.storage.postgresql.models import User, Session


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

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_session(
            self,
            user_id: str,
            refresh_token_hash: str,
            expires_at: datetime,
            is_revoked: bool
    ) -> None:
        session = Session(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
            is_revoked=is_revoked,
        )

        self.session.add(session)
        await self.session.commit()