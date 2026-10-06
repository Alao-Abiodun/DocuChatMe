from lib.events_lib import app_events
from events.auth_events import AUTH_EVENTS
from lib.password_lib import hash_password, verify_password
from lib.tokens_lib import generate_access_token, generate_referesh_token, verify_refresh_token
from datetime import datetime, timedelta, timezone
from lib.prisma_lib import prisma
import hashlib
import jwt

async def register(data: dict) -> dict:
    existing_user = await prisma.user.find_unique(
        where={ "email": data["email"].lower().strip() },
    )
    if existing_user:
        raise ValueError("Email already registered")

    password_hash = await hash_password(data["password"])
    user = await prisma.user.create(
        data={
            "name": data["name"],
            "email": data["email"].lower().strip(),
            "passwordHash": password_hash
        }
    )
    default_role = await prisma.role.find_first(where={"isDefault": True})

    if default_role:
        await prisma.userrole.create(
            data={"userId": user.id, "roleId": default_role.id}
        )

    # Emit and move on. Don't wait for listeners
    app_events.emit(AUTH_EVENTS["USER_REGISTERED"], {
        "id": user.id,
        "email": user.email,
        "tier": user.tier
    })

    return {"id": user.id, "email": user.email, "tier": user.tier}


async def login(data: dict) -> dict:
    user = await prisma.user.find_unique(
        where={
            "email": data["email"].lower().strip(),
        }
    )

    # Same error for "user not found" and "wrong password"
    # This prevents user enumeration attacks
    if not user or not user.isActive:
        raise ValueError("Invalid credentials!")

    valid = await verify_password(data["password"], user.passwordHash)
    if not valid:
        raise ValueError("Invalid credentials")

    # Generate tokens
    access_token = generate_access_token(user)
    refresh_token = generate_referesh_token(user)

    # Store the referesh token hash (never store the raw token)
    token_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()

    await prisma.refreshtoken.create(
        data={
            "userId": user.id,
            "token": token_hash,
            "expiresAt": datetime.now(timezone.utc) + timedelta(days=7)
        }
    )

    app_events.emit(AUTH_EVENTS["USER_LOGGED_IN"], {
        "userId": user.id
    })

    return {
        "user": {"id": user.id, "email": user.email, "tier": user.tier},
        "accessToken": access_token,
        "refreshToken": refresh_token,
    }

async def refresh(raw_refresh_token: str) -> dict:
    # Verify the JWT signature and expiration
    try:
        payload = verify_refresh_token(raw_refresh_token)
    except jwt.PyJWTError:
        raise ValueError("Invalid refresh token")

    if payload["type"] != "refresh":
        raise ValueError("Invalid token type")

    # Check if this token exists in the database (not revoked)
    token_hash = hashlib.sha256(raw_refresh_token.encode("utf-8")).hexdigest()

    stored = await prisma.refreshToken.find_unique(where={"token": token_hash})

    if not stored or stored.expiresAt < datetime.now(timezone.utc):
        raise ValueError("Refresh token expired or revoked")

    # Get the user
    user = await prisma.user.find_unique(where={"id": payload["sub"]})
    if not user or not user.isActive:
        raise ValueError("User not found or inactive")

    new_access_token = generate_access_token(user)
    new_refresh_token = generate_referesh_token(user)
    new_hash = hashlib.sha256(new_refresh_token.encode("utf-8")).hexdigest()

    await prisma.refreshToken.create(
        data={
            "userId": user.id,
            "token": new_hash,
            "expiresAt": datetime.now(timezone.utc) + timedelta(days=7)
        }
    )

    return {"accessToken": new_access_token, "refreshToken": new_refresh_token}


async def logout(raw_refresh_token: str) -> None:
    token_hash = hashlib.sha256(raw_refresh_token.encode("utf-8")).hexdigest()

    # Delete the token. If it doesn't exist, that's fine.
    await prisma.refreshToken.delete_many(where={"token": token_hash})

