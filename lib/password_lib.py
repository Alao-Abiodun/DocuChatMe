import asyncio
import bcrypt

SALT_ROUNDS = 12


def _hash_sync(plaintext: str) -> str:
    salt = bcrypt.gensalt(rounds=SALT_ROUNDS)
    return bcrypt.hashpw(plaintext.encode("utf-8"), salt).decode("utf-8")


async def hash_password(plaintext: str) -> str:
    return await asyncio.to_thread(_hash_sync, plaintext)


async def verify_password(plaintext: str, hashed: str) -> bool:
    return await asyncio.to_thread(
        bcrypt.checkpw, plaintext.encode("utf-8"), hashed.encode("utf-8")
    )