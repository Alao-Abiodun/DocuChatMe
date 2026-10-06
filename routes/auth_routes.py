from fastapi import APIRouter, Request
from services import auth_service

router = APIRouter()

@router.post("/register", status_code=201)
async def register_route(request: Request):
    body = await request.json()
    user = await auth_service.register(body)
    return {"user": user}


@router.post("/login", status_code=200)
async def login_route(request: Request):
    body = await request.json()
    body["deviceInfo"] = request.headers.get("user-agent")
    result = await auth_service.login(body)
    return result;

@router.post("/refresh")
async def refresh_route(request: Request):
    body = await request.json()
    result = await auth_service.refresh(body["refreshToken"])
    return result


@router.post("/logout")
async def logout_route(request: Request):
    body = await request.json()
    await auth_service.logout(body["refreshToken"])
    return {"message": "Logged out"}
