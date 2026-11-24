from datetime import datetime, timedelta, timezone

import jwt

from pwdlib import PasswordHash

from app.core.config import settings


password_hasher = PasswordHash.recommended()


# =========================================================
# CONTRASEÑAS
# =========================================================

def hash_password(password: str) -> str:

    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return password_hasher.verify(
        plain_password,
        hashed_password
    )


# =========================================================
# JWT
# =========================================================

def create_access_token(user_id: int) -> str:

    now = datetime.now(timezone.utc)

    expiration = now + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expiration
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def decode_access_token(token: str) -> dict:

    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )