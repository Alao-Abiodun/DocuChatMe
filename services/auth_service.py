import hashlib
from datetime import datetime, timedelta, timezone

import jwt

from events.auth_events import AUTH_EVENTS
from lib.errors_lib import ConflictError, UnauthorizedError
from lib.events_lib import app_events
from lib.password_lib import hash_password, verify_password
from lib.tokens_lib import (
    generate_access_token,
    generate_referesh_token,
    verify_refresh_token,
)
from repositories import refresh_token_repository, role_repository, user_repository

REFRESH_TOKEN_TTL = timedelta(days=7)


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


async def _issue_refresh_token(user) -> str:
    raw_token = generate_referesh_token(user)
    await refresh_token_repository.create(
        user.id,
        _hash_token(raw_token),
        datetime.now(timezone.utc) + REFRESH_TOKEN_TTL,
    )
    return raw_token


async def register(name: str, email: str, password: str) -> dict:
    normalized_email = email.lower().strip()

    if await user_repository.find_by_email(normalized_email):
        raise ConflictError("Email already registered")

    user = await user_repository.create(
        {
            "name": name,
            "email": normalized_email,
            "passwordHash": await hash_password(password),
        }
    )

    default_role = await role_repository.find_default()
    if default_role:
        await role_repository.assign_to_user(user.id, default_role.id, user.id)

    # Emit and move on. Don't wait for listeners
    app_events.emit(
        AUTH_EVENTS["USER_REGISTERED"],
        {"id": user.id, "email": user.email, "tier": user.tier},
    )

    return {"id": user.id, "email": user.email, "tier": user.tier}


async def login(email: str, password: str) -> dict:
    user = await user_repository.find_by_email(email.lower().strip())

    # Same error for "user not found" and "wrong password".
    # This prevents user enumeration attacks.
    if not user or not user.isActive:
        raise UnauthorizedError("Invalid credentials")

    if not await verify_password(password, user.passwordHash):
        raise UnauthorizedError("Invalid credentials")

    access_token = generate_access_token(user)
    refresh_token = await _issue_refresh_token(user)

    app_events.emit(AUTH_EVENTS["USER_LOGGED_IN"], {"userId": user.id})

    return {
        "user": {"id": user.id, "email": user.email, "tier": user.tier},
        "accessToken": access_token,
        "refreshToken": refresh_token,
    }


async def refresh(raw_refresh_token: str) -> dict:
    try:
        payload = verify_refresh_token(raw_refresh_token)
    except jwt.PyJWTError:
        raise UnauthorizedError("Invalid refresh token")

    if payload["type"] != "refresh":
        raise UnauthorizedError("Invalid token type")

    # Confirm the token still exists in the database (i.e. was not revoked)
    stored = await refresh_token_repository.find_by_token(
        _hash_token(raw_refresh_token)
    )
    if not stored or stored.expiresAt < datetime.now(timezone.utc):
        raise UnauthorizedError("Refresh token expired or revoked")

    user = await user_repository.find_by_id(payload["sub"])
    if not user or not user.isActive:
        raise UnauthorizedError("User not found or inactive")

    access_token = generate_access_token(user)
    refresh_token = await _issue_refresh_token(user)

    app_events.emit(AUTH_EVENTS["TOKEN_REFRESHED"], {"userId": user.id})

    return {"accessToken": access_token, "refreshToken": refresh_token}


async def logout(raw_refresh_token: str) -> None:
    # Deleting a token that does not exist is fine — logout stays idempotent.
    await refresh_token_repository.delete_by_token(_hash_token(raw_refresh_token))
