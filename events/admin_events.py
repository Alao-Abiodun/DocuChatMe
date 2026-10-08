from lib.events_lib import app_events
from repositories import usage_log_repository


@app_events.on("admin:role-assigned")
async def log_role_assigned(data: dict):
    try:
        await usage_log_repository.create(data["assignedBy"], action="role_assigned")
    except Exception as error:
        print(f"Failed to log role assignment: {error}")


@app_events.on("admin:role-revoked")
async def log_role_revoked(data: dict):
    try:
        await usage_log_repository.create(data["revokedBy"], action="role_revoked")
    except Exception as error:
        print(f"Failed to log role revocation: {error}")
