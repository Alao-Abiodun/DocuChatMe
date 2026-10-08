from lib.prisma_lib import prisma


async def create(data: dict, client=None):
    db = client or prisma
    return await db.message.create(data=data)


async def count_by_conversation_ids(conversation_ids: list[str], client=None):
    db = client or prisma
    return await db.message.group_by(
        by=["conversationId"],
        count=True,
        where={"conversationId": {"in": conversation_ids}},
    )
