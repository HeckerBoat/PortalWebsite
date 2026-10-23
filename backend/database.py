"""数据库初始化：使用 SQLModel + SQLite。"""
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session

from backend.config import settings, BASE_DIR

# 确保 db 目录存在
db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
if not db_path.is_absolute():
    db_path = BASE_DIR / db_path
db_path.parent.mkdir(parents=True, exist_ok=True)

# 数据库 URL（绝对路径）
DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    """创建所有表。"""
    # 导入所有模型以触发注册
    from backend.models import user, html_file, system_config  # noqa: F401
    SQLModel.metadata.create_all(engine)


def get_session():
    """获取数据库会话（依赖注入用）。"""
    with Session(engine) as session:
        yield session
