import os
from datetime import datetime, timedelta, timezone
import jwt
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
REFRESH_TOKEN_SECRET = os.getenv("REFRESH_TOKEN_SECRET")

def generate_access_token(user) -> str:
    payload = {
        "sub": user.id,
        "role": user.role,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
    }
    return jwt.encode(payload, ACCESS_TOKEN_SECRET, algorithm="HS256")

def generate_referesh_token(user) -> str:
    payload = {
        "sub": user.id,
        "role": user.role,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=7)
    }
    return jwt.encode(payload, REFRESH_TOKEN_SECRET, algorithm="HS256")

def verify_access_token(token: str) -> dict:
    return jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=["HS256"])

def verify_refresh_token(token: str) -> dict:
    return jwt.decode(token, REFRESH_TOKEN_SECRET, algorithms=["HS256"])