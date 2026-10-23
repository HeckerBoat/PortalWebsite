"""密码二次哈希与 JWT 工具。"""
import hashlib
import secrets
import time
from typing import Optional, Tuple

import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from backend.config import settings


def hash_password(password: str) -> str:
    """二次哈希：先用 werkzeug 哈希，再叠加 sha256 盐值哈希。"""
    first_hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)
    salt = secrets.token_hex(16)
    second_hash = hashlib.sha256(f"{first_hash}{salt}".encode()).hexdigest()
    # 存储格式：salt$second_hash$first_hash
    return f"{salt}${second_hash}${first_hash}"


def verify_password(password: str, stored: str) -> bool:
    """校验密码：还原二次哈希。"""
    try:
        salt, second_hash, first_hash = stored.split("$", 2)
    except ValueError:
        return False
    # 校验二次哈希
    computed = hashlib.sha256(f"{first_hash}{salt}".encode()).hexdigest()
    if computed != second_hash:
        return False
    # 再用 werkzeug 校验一次
    return check_password_hash(first_hash, password)


def create_token(user_id: int, username: str, role: str) -> str:
    """生成 JWT token。"""
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": int(time.time()) + settings.JWT_EXPIRE_HOURS * 3600,
        "iat": int(time.time()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> Optional[dict]:
    """解析 JWT token，失败返回 None。"""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
