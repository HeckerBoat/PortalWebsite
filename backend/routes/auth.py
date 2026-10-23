"""认证路由：注册、登录、当前用户信息。"""
from flask import Blueprint, request

from backend.services.auth_service import register_user, login_user, get_current_user
from backend.utils.response import success, error

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    email = (data.get("email") or "").strip() or None
    phone = (data.get("phone") or "").strip() or None

    if not username or not password:
        return error("用户名和密码不能为空")
    if len(password) < 6:
        return error("密码长度至少 6 位")
    if not email and not phone:
        return error("邮箱或手机号至少填写一项")

    ok, msg, user = register_user(username, password, email, phone)
    if not ok:
        return error(msg)
    return success({"id": user.id, "username": user.username}, msg)


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    account = (data.get("account") or "").strip()
    password = data.get("password") or ""
    if not account or not password:
        return error("账号和密码不能为空")
    ok, msg, info = login_user(account, password)
    if not ok:
        return error(msg)
    return success(info, msg)


@auth_bp.get("/me")
def me():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else auth_header
    user = get_current_user(token)
    if not user:
        return error("未登录", code=401, http_status=401)
    return success({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "is_active": user.is_active,
    })
