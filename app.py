"""HTML 自动管理网站 - 启动入口。"""
import os
import sys
from pathlib import Path

from flask import Flask, send_from_directory, redirect
from flask_cors import CORS

# 确保项目根目录在 sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import settings  # noqa: E402
from backend.database import init_db  # noqa: E402
from backend.services.auth_service import init_admin  # noqa: E402
from backend.services.html_service import sync_scan  # noqa: E402
from backend.routes.auth import auth_bp  # noqa: E402
from backend.routes.html_manager import html_bp  # noqa: E402
from backend.routes.user_manager import user_mgr_bp  # noqa: E402
from backend.routes.system_config import config_bp  # noqa: E402


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    CORS(app, supports_credentials=True)

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(html_bp)
    app.register_blueprint(user_mgr_bp)
    app.register_blueprint(config_bp)

    # ---- 静态 HTML 文件服务：供生成的 URL 访问 ----
    scan_root = Path(settings.HTML_SCAN_DIR)
    if not scan_root.is_absolute():
        scan_root = BASE_DIR / scan_root

    @app.route("/static/html/<path:filename>")
    def serve_html(filename: str):
        """服务扫描目录下的 HTML 文件。"""
        return send_from_directory(str(scan_root), filename)

    # ---- 前端构建产物服务 ----
    frontend_dist = BASE_DIR / "Frontend" / "dist"
    if frontend_dist.exists():
        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_frontend(path: str):
            """服务 Vue 构建产物，支持 history 路由。"""
            # API 请求不拦截
            if path.startswith("api/") or path.startswith("static/html/"):
                return ("", 404)
            target = frontend_dist / path
            if path and target.exists() and target.is_file():
                return send_from_directory(str(frontend_dist), path)
            return send_from_directory(str(frontend_dist), "index.html")

    # ---- 健康检查 ----
    @app.get("/api/health")
    def health():
        return {"code": 0, "message": "ok", "data": {"status": "running"}}

    return app


def main():
    print("=" * 60)
    print("  HTML 自动管理网站 启动中...")
    print("=" * 60)

    # 1. 初始化数据库
    init_db()
    print("[启动] 数据库初始化完成")

    # 2. 初始化管理员
    init_admin()

    # 3. 启动时自动扫描一次
    try:
        result = sync_scan()
        print(f"[启动] 首次扫描完成: {result}")
    except Exception as e:
        print(f"[启动] 首次扫描异常: {e}")

    app = create_app()
    print(f"[启动] 服务地址: http://{settings.FLASK_HOST}:{settings.FLASK_PORT}")
    print(f"[启动] 前端目录: {BASE_DIR / 'Frontend'}")
    print("=" * 60)

    app.run(
        host=settings.FLASK_HOST,
        port=settings.FLASK_PORT,
        debug=settings.FLASK_DEBUG,
        use_reloader=False,
    )


if __name__ == "__main__":
    main()
