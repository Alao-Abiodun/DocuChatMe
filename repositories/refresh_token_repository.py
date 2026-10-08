from lib.prisma_lib import prisma


async def create(user_id: str, token_hash: str, expires_at, client=None):
    db = client or prisma
    return await db.refreshtoken.create(
        data={"userId": user_id, "token": token_hash, "expiresAt": expires_at}
    )


async def find_by_token(token_hash: str, client=None):
    db = client or prisma
    return await db.refreshtoken.find_unique(where={"token": token_hash})


async def delete_by_token(token_hash: str, client=None):
    db = client or prisma
    return await db.refreshtoken.delete_many(where={"token": token_hash})
