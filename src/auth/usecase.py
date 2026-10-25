from pwdlib import PasswordHash

from src.auth.domain.schemas import RegisterRequest
from src.auth.infrastructure.storage.postgresql.repository import AuthRepository


class Register:
    def __init__(self, repository: AuthRepository):
        self.repository = repository
        self.password_hasher = PasswordHash.recommended()

    async def execute(self, req: RegisterRequest) -> str:
        pass_hash = self.password_hasher.hash(req.password)

        id_ = await self.repository.register(
            email=req.email,
            profile_id=req.profile_id,
            pass_hash=pass_hash
        )

        return id_
