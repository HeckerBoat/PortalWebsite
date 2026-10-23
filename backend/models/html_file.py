"""HTML 文件模型。"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class HtmlFile(SQLModel, table=True):
    __tablename__ = "html_files"

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=255, description="文件名（含扩展名）")
    relative_path: str = Field(max_length=1024, description="相对于扫描根目录的路径")
    absolute_path: str = Field(max_length=2048, description="绝对路径")
    url: str = Field(max_length=2048, description="访问该 HTML 的 URL")
    title: Optional[str] = Field(default=None, max_length=255, description="页面标题（从 <title> 提取）")
    description: Optional[str] = Field(default=None, max_length=1024, description="备注描述")
    file_size: int = Field(default=0, description="文件大小（字节）")
    last_modified: datetime = Field(default_factory=datetime.now, description="文件最后修改时间")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
