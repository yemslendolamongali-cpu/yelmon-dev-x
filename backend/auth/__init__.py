"""YELMON Dev X - Authentification (hash + JWT).

© 2026 Yems junior lendola — All Rights Reserved.
PROPRIETARY SOFTWARE — Unauthorized copying, distribution, reverse
engineering, or reproduction of this code is strictly prohibited.
"""

import hashlib
import hmac
import base64
import json
import time
import os

try:
    import jwt as pyjwt
    HAS_PYJWT = True
except Exception:
    HAS_PYJWT = False

_SALT_LEN = 16


def hash_password(password: str, salt: bytes = None) -> str:
    """Hash un mot de passe (PBKDF2-SHA256)."""
    if salt is None:
        salt = os.urandom(_SALT_LEN)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return "pbkdf2$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(dk).decode()


def verify_password(stored: str, password: str) -> bool:
    try:
        _, salt_b64, hash_b64 = stored.split("$")
        salt = base64.b64decode(salt_b64)
        return hmac.compare_digest(hash_password(password, salt), stored)
    except Exception:
        return False


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def create_token(payload: dict, secret: str, expires_hours: int = 24) -> str:
    body = dict(payload)
    body["iat"] = int(time.time())
    body["exp"] = int(time.time()) + expires_hours * 3600
    if HAS_PYJWT:
        return pyjwt.encode(body, secret, algorithm="HS256")
    header = _b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload_b64 = _b64url(json.dumps(body).encode())
    signing = f"{header}.{payload_b64}".encode()
    sig = _b64url(hmac.new(secret.encode(), signing, hashlib.sha256).digest())
    return f"{header}.{payload_b64}.{sig}"


def decode_token(token: str, secret: str):
    try:
        if HAS_PYJWT:
            return pyjwt.decode(token, secret, algorithms=["HS256"])
        header_b64, payload_b64, sig_b64 = token.split(".")
        signing = f"{header_b64}.{payload_b64}".encode()
        expected = _b64url(hmac.new(secret.encode(), signing, hashlib.sha256).digest())
        if not hmac.compare_digest(expected, sig_b64):
            return None
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "=="))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None
