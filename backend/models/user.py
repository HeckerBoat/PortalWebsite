"""用户模型。"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=64, description="用户名")
    email: Optional[str] = Field(default=None, index=True, max_length=128, description="邮箱")
    phone: Optional[str] = Field(default=None, index=True, max_length=20, description="手机号")
    password_hash: str = Field(max_length=512, description="二次哈希后的密码密文")
    role: str = Field(default="user", max_length=20, description="角色：admin/user")
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
