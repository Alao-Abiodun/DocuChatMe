from lib.events_lib import app_events
from lib.prisma_lib import prisma


@app_events.on("admin:role-assigned")
async def log_role_assigned(data: dict):
    try:
        await prisma.usagelog.create(
            data={
                "userId": data["assignedBy"], "action": "role_assigned", "tokens": 0, "costUsd": 0,
            }
        )
    except Exception as error:
        print(f"Failed to log role assignment: {error}")


@app_events.on("admin:role-revoked")
async def log_role_revoked(data: dict):
    try:
        await prisma.usagelog.create(
            data={
                "userId": data["revokedBy"], "action": "role_revoked", "tokens": 0, "costUsd": 0,
            }
        )
    except Exception as error:
        print(f"Failed to log role revocation: {error}")