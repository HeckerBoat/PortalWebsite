"""路由包。"""
from functools import wraps
from flask import request

from backend.services.auth_service import get_current_user
from backend.utils.response import error


def login_required(f):
    """登录校验装饰器。"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else auth_header
        if not token:
            return error("未提供认证 token", code=401, http_status=401)
        user = get_current_user(token)
        if not user:
            return error("登录已过期，请重新登录", code=401, http_status=401)
        request.current_user = user  # type: ignore
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """管理员权限校验装饰器。"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else auth_header
        if not token:
            return error("未提供认证 token", code=401, http_status=401)
        user = get_current_user(token)
        if not user:
            return error("登录已过期，请重新登录", code=401, http_status=401)
        if user.role != "admin":
            return error("需要管理员权限", code=403, http_status=403)
        request.current_user = user  # type: ignore
        return f(*args, **kwargs)
    return decorated
