"""认证相关服务。"""
from datetime import datetime
from typing import Optional, Tuple

from sqlmodel import Session, select
from werkzeug.exceptions import Unauthorized

from backend.config import settings
from backend.database import engine
from backend.models import User
from backend.utils.security import hash_password, verify_password, create_token, decode_token


def init_admin() -> None:
    """初始化管理员账号。"""
    with Session(engine) as session:
        stmt = select(User).where(User.username == settings.ADMIN_USERNAME)
        existing = session.exec(stmt).first()
        if existing:
            return
        admin = User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            phone=settings.ADMIN_PHONE,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            role="admin",
            is_active=True,
        )
        session.add(admin)
        session.commit()
        print(f"[auth] 已创建管理员账号: {settings.ADMIN_USERNAME}")


def register_user(username: str, password: str, email: Optional[str] = None,
                  phone: Optional[str] = None) -> Tuple[bool, str, Optional[User]]:
    """用户注册。"""
    with Session(engine) as session:
        # 用户名重复检查
        if session.exec(select(User).where(User.username == username)).first():
            return False, "用户名已存在", None
        if email and session.exec(select(User).where(User.email == email)).first():
            return False, "邮箱已被注册", None
        if phone and session.exec(select(User).where(User.phone == phone)).first():
            return False, "手机号已被注册", None

        user = User(
            username=username,
            email=email,
            phone=phone,
            password_hash=hash_password(password),
            role="user",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return True, "注册成功", user


def login_user(account: str, password: str) -> Tuple[bool, str, Optional[dict]]:
    """用户登录：账号可以是用户名/邮箱/手机号。"""
    with Session(engine) as session:
        stmt = select(User).where(
            (User.username == account) | (User.email == account) | (User.phone == account)
        )
        user = session.exec(stmt).first()
        if not user:
            return False, "账号不存在", None
        if not user.is_active:
            return False, "账号已被禁用", None
        if not verify_password(password, user.password_hash):
            return False, "密码错误", None

        token = create_token(user.id, user.username, user.role)
        return True, "登录成功", {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
            },
        }


def get_current_user(token: str) -> Optional[User]:
    """从 token 获取当前用户。"""
    payload = decode_token(token)
    if not payload:
        return None
    with Session(engine) as session:
        return session.get(User, payload["user_id"])


def require_admin(token: str) -> User:
    """要求管理员权限，否则抛异常。"""
    user = get_current_user(token)
    if not user:
        raise Unauthorized("未登录或登录已过期")
    if user.role != "admin":
        raise PermissionError("需要管理员权限")
    return user


def require_user(token: str) -> User:
    """要求已登录用户。"""
    user = get_current_user(token)
    if not user:
        raise Unauthorized("未登录或登录已过期")
    return user
