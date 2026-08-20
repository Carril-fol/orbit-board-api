from fastapi.concurrency import run_in_threadpool
from pwdlib import PasswordHash

class PasswordManager:
    _password_hash = PasswordHash.recommended()

    @classmethod
    async def hash(cls, password: str) -> str:
        return await run_in_threadpool(cls._password_hash.hash, password)
    
    @classmethod
    async def verify(cls, password: str, password_hashed: str) -> bool:
        return await run_in_threadpool(cls._password_hash.verify, password, password_hashed)
