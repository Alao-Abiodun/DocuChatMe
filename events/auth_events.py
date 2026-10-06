from lib.events_lib import app_events
from lib.prisma_lib import prisma

AUTH_EVENTS = {
    "USER_REGISTERED": "auth:user-registered",
    "USER_LOGGED_IN": "auth:user-logged-in",
    "USER_LOGGED_OUT": "auth:user-logged-out",
    "TOKEN_REFRESHED": "auth:token-refreshed",
    "LOGIN_FAILED": "auth:login-failed",
}

@app_events.on(AUTH_EVENTS["USER_REGISTERED"])
async def log_signup(user: dict):
    try:
        await prisma.usagelog.create(
            data={"userId": user["id"], "action": "signup", "tokens": 0, "costUsd": 0}
        )
    except Exception as error:
        print(f"Failed to log signup: {error}")


@app_events.on(AUTH_EVENTS["USER_REGISTERED"])
async def create_welcome_conversation(user: dict):
    try:
        await prisma.conversation.create(
            data={"userId": user["id"], "title": "Welcome to DocuChat"}
        )
    except Exception as error:
        print(f"Failed to create welcome conversation: {error}")


@app_events.on(AUTH_EVENTS["USER_LOGGED_IN"])
async def log_login(data: dict):
    try:
        await prisma.usagelog.create(
            data={"userId": data["userId"], "action": "login", "tokens": 0, "costUsd": 0}
        )
    except Exception as error:
        print(f"Failed to log login: {error}")


@app_events.on(AUTH_EVENTS["LOGIN_FAILED"])
async def log_failed_login(data: dict):
    print(f"Failed login attempt for {data['email']} from {data.get('deviceInfo')}")