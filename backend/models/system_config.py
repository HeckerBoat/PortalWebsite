"""系统配置模型。"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class SystemConfig(SQLModel, table=True):
    __tablename__ = "system_configs"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(index=True, unique=True, max_length=128, description="配置键")
    value: str = Field(default="", max_length=4096, description="配置值")
    description: Optional[str] = Field(default=None, max_length=512, description="配置说明")
    updated_at: datetime = Field(default_factory=datetime.now)
