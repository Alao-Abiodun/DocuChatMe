from lib.prisma_lib import prisma


async def find_many(where: dict, order_by: dict, skip: int, take: int, client=None):
    db = client or prisma
    return await db.document.find_many(
        where=where, order=order_by, skip=skip, take=take
    )


async def count(where: dict, client=None):
    db = client or prisma
    return await db.document.count(where=where)


async def find_by_id(document_id: str, client=None):
    db = client or prisma
    return await db.document.find_unique(where={"id": document_id})


async def find_active_owned(document_id: str, user_id: str, client=None):
    db = client or prisma
    return await db.document.find_first(
        where={"id": document_id, "userId": user_id, "deletedAt": None}
    )


async def create(data: dict, client=None):
    db = client or prisma
    return await db.document.create(data=data)


async def update(document_id: str, data: dict, client=None):
    db = client or prisma
    return await db.document.update(where={"id": document_id}, data=data)


async def delete_chunks(document_id: str, client=None):
    db = client or prisma
    return await db.chunk.delete_many(where={"documentId": document_id})


async def create_chunks(chunks: list[dict], client=None):
    db = client or prisma
    return await db.chunk.create_many(data=chunks)
