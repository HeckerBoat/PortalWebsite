"""应用配置：从 .env 读取环境变量。"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 加载 .env
load_dotenv(BASE_DIR / ".env")


class Settings:
    # 服务
    FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() in ("1", "true", "yes")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key_change_me")

    # 数据库
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db' / 'app.db'}")

    # 管理员
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "1q2w3e4r")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PHONE: str = os.getenv("ADMIN_PHONE", "13800000000")

    # HTML 扫描目录
    HTML_SCAN_DIR: str = os.getenv("HTML_SCAN_DIR", "Frontend")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "jwt_secret_change_me")
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))


settings = Settings()
