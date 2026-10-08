from lib.prisma_lib import prisma


async def list_with_latest_message(user_id: str, skip: int, take: int, client=None):
    db = client or prisma
    return await db.conversation.find_many(
        where={"userId": user_id},
        order={"updatedAt": "desc"},
        skip=skip,
        take=take,
        include={
            "messages": {
                "order_by": {"createdAt": "desc"},
                "take": 1,
            }
        },
    )


async def count(user_id: str, client=None):
    db = client or prisma
    return await db.conversation.count(where={"userId": user_id})


async def find_owned(conversation_id: str, user_id: str, client=None):
    db = client or prisma
    return await db.conversation.find_first(
        where={"id": conversation_id, "userId": user_id}
    )


async def create(user_id: str, title: str, client=None):
    db = client or prisma
    return await db.conversation.create(data={"userId": user_id, "title": title})


async def touch(conversation_id: str, updated_at, client=None):
    db = client or prisma
    return await db.conversation.update(
        where={"id": conversation_id}, data={"updatedAt": updated_at}
    )
