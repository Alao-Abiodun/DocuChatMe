from lib.prisma_lib import prisma


async def create(
    user_id: str,
    action: str,
    tokens: int = 0,
    cost_usd: float = 0,
    metadata: str | None = None,
    client=None,
):
    db = client or prisma
    data = {
        "userId": user_id,
        "action": action,
        "tokens": tokens,
        "costUsd": cost_usd,
    }
    if metadata is not None:
        data["metadata"] = metadata

    return await db.usagelog.create(data=data)
