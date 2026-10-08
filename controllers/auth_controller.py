from services import auth_service
from validators.auth_validator import (
    LoginBody,
    RefreshBody,
    RegisterBody,
)


async def register(body: RegisterBody) -> dict:
    user = await auth_service.register(body.name, body.email, body.password)
    return {"user": user}


async def login(body: LoginBody) -> dict:
    return await auth_service.login(body.email, body.password)


async def refresh(body: RefreshBody) -> dict:
    return await auth_service.refresh(body.refreshToken)


async def logout(body: RefreshBody) -> dict:
    await auth_service.logout(body.refreshToken)
    return {"message": "Logged out"}
