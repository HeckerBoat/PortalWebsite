"""统一响应封装。"""
from flask import jsonify
from typing import Any, Optional


def success(data: Any = None, message: str = "ok", code: int = 0):
    return jsonify({"code": code, "message": message, "data": data})


def error(message: str = "error", code: int = -1, data: Any = None, http_status: int = 200):
    return jsonify({"code": code, "message": message, "data": data}), http_status
