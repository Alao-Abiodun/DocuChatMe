from fastapi import APIRouter

from controllers import auth_controller
from validators.auth_validator import LoginBody, RefreshBody, RegisterBody

router = APIRouter()


@router.post("/register", status_code=201)
async def register_route(body: RegisterBody):
    return await auth_controller.register(body)


@router.post("/login")
async def login_route(body: LoginBody):
    return await auth_controller.login(body)


@router.post("/refresh")
async def refresh_route(body: RefreshBody):
    return await auth_controller.refresh(body)


@router.post("/logout")
async def logout_route(body: RefreshBody):
    return await auth_controller.logout(body)
