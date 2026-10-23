"""用户管理路由：管理员可对用户任意信息进行任意修改。"""
from datetime import datetime
from flask import Blueprint, request
from sqlmodel import Session, select

from backend.database import engine
from backend.models import User
from backend.routes import admin_required
from backend.utils.security import hash_password
from backend.utils.response import success, error

user_mgr_bp = Blueprint("user_mgr", __name__, url_prefix="/api/users")


def _user_dict(u: User) -> dict:
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "phone": u.phone,
        "role": u.role,
        "is_active": u.is_active,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "updated_at": u.updated_at.isoformat() if u.updated_at else None,
    }


@user_mgr_bp.get("")
@admin_required
def list_users():
    keyword = request.args.get("keyword", "").strip()
    with Session(engine) as session:
        stmt = select(User)
        if keyword:
            kw = f"%{keyword}%"
            stmt = stmt.where(
                (User.username.like(kw)) | (User.email.like(kw)) | (User.phone.like(kw))
            )
        stmt = stmt.order_by(User.id.desc())
        users = session.exec(stmt).all()
        return success([_user_dict(u) for u in users])


@user_mgr_bp.put("/<int:user_id>")
@admin_required
def update_user(user_id: int):
    """管理员修改用户任意信息。"""
    data = request.get_json(silent=True) or {}
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return error("用户不存在")
        # 可修改字段
        if "username" in data and data["username"]:
            user.username = data["username"]
        if "email" in data:
            user.email = data["email"] or None
        if "phone" in data:
            user.phone = data["phone"] or None
        if "password" in data and data["password"]:
            user.password_hash = hash_password(data["password"])
        if "role" in data and data["role"] in ("admin", "user"):
            user.role = data["role"]
        if "is_active" in data:
            user.is_active = bool(data["is_active"])
        user.updated_at = datetime.now()
        session.add(user)
        session.commit()
        session.refresh(user)
        return success(_user_dict(user), "更新成功")


@user_mgr_bp.delete("/<int:user_id>")
@admin_required
def delete_user(user_id: int):
    current = getattr(request, "current_user", None)
    if current and current.id == user_id:
        return error("不能删除自己")
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return error("用户不存在")
        if user.username == "admin":
            return error("不能删除超级管理员")
        session.delete(user)
        session.commit()
        return success(None, "删除成功")


@user_mgr_bp.post("")
@admin_required
def create_user():
    """管理员创建用户。"""
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return error("用户名和密码不能为空")
    with Session(engine) as session:
        if session.exec(select(User).where(User.username == username)).first():
            return error("用户名已存在")
        user = User(
            username=username,
            email=data.get("email") or None,
            phone=data.get("phone") or None,
            password_hash=hash_password(password),
            role=data.get("role", "user"),
            is_active=bool(data.get("is_active", True)),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return success(_user_dict(user), "创建成功")
