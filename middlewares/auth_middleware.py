from fastapi import Header, HTTPException
import jwt

from lib.tokens_lib import verify_access_token

async def authenticate(authorization: str = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")

    token = authorization.split(" ")[1]

    try:
        payload = verify_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload["type"] != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    return {"id": payload["sub"], "role": payload["role"]}
                        