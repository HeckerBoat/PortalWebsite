"""系统配置路由：前端参数读写，持久化到 SQLite。"""
from datetime import datetime
from flask import Blueprint, request
from sqlmodel import Session, select

from backend.database import engine
from backend.models import SystemConfig
from backend.routes import login_required
from backend.utils.response import success, error

config_bp = Blueprint("config", __name__, url_prefix="/api/config")


@config_bp.get("")
@login_required
def get_all():
    """获取所有配置项。"""
    with Session(engine) as session:
        configs = session.exec(select(SystemConfig).order_by(SystemConfig.key)).all()
        return success([{"key": c.key, "value": c.value, "description": c.description} for c in configs])


@config_bp.get("/<key>")
@login_required
def get_one(key: str):
    with Session(engine) as session:
        c = session.exec(select(SystemConfig).where(SystemConfig.key == key)).first()
        if not c:
            return error("配置项不存在")
        return success({"key": c.key, "value": c.value, "description": c.description})


@config_bp.put("/<key>")
@login_required
def set_one(key: str):
    """新增或更新配置项。"""
    data = request.get_json(silent=True) or {}
    value = data.get("value", "")
    description = data.get("description")
    with Session(engine) as session:
        c = session.exec(select(SystemConfig).where(SystemConfig.key == key)).first()
        if c:
            c.value = str(value)
            if description is not None:
                c.description = description
            c.updated_at = datetime.now()
        else:
            c = SystemConfig(key=key, value=str(value), description=description)
        session.add(c)
        session.commit()
        return success({"key": c.key, "value": c.value}, "保存成功")


@config_bp.delete("/<key>")
@login_required
def delete_one(key: str):
    with Session(engine) as session:
        c = session.exec(select(SystemConfig).where(SystemConfig.key == key)).first()
        if not c:
            return error("配置项不存在")
        session.delete(c)
        session.commit()
        return success(None, "删除成功")
