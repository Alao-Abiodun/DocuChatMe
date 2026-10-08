from lib.prisma_lib import prisma


async def find_by_email(email: str, client=None):
    db = client or prisma
    return await db.user.find_unique(where={"email": email})


async def find_by_id(user_id: str, client=None):
    db = client or prisma
    return await db.user.find_unique(where={"id": user_id})


async def create(data: dict, client=None):
    db = client or prisma
    return await db.user.create(data=data)
