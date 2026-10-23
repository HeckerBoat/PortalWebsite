"""HTML 文件管理路由：扫描同步、列表、详情、更新、删除。"""
from flask import Blueprint, request

from backend.routes import login_required
from backend.services import html_service
from backend.utils.response import success, error

html_bp = Blueprint("html", __name__, url_prefix="/api/html")


@html_bp.post("/scan")
@login_required
def scan():
    """手动触发扫描同步。"""
    try:
        result = html_service.sync_scan()
        return success(result, "扫描同步完成")
    except Exception as e:
        print(f"[html_manager] 扫描异常: {e}")
        return error(f"扫描失败: {e}")


@html_bp.get("/list")
@login_required
def list_files():
    keyword = request.args.get("keyword", "").strip() or None
    files = html_service.list_html_files(keyword)
    data = [{
        "id": f.id,
        "filename": f.filename,
        "relative_path": f.relative_path,
        "url": f.url,
        "title": f.title,
        "description": f.description,
        "file_size": f.file_size,
        "last_modified": f.last_modified.isoformat() if f.last_modified else None,
        "updated_at": f.updated_at.isoformat() if f.updated_at else None,
    } for f in files]
    return success(data)


@html_bp.get("/<int:file_id>")
@login_required
def detail(file_id: int):
    f = html_service.get_html_file(file_id)
    if not f:
        return error("文件不存在")
    return success({
        "id": f.id,
        "filename": f.filename,
        "relative_path": f.relative_path,
        "absolute_path": f.absolute_path,
        "url": f.url,
        "title": f.title,
        "description": f.description,
        "file_size": f.file_size,
        "last_modified": f.last_modified.isoformat() if f.last_modified else None,
    })


@html_bp.put("/<int:file_id>")
@login_required
def update(file_id: int):
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    description = data.get("description")
    url = data.get("url")
    f = html_service.update_html_file(file_id, title=title, description=description, url=url)
    if not f:
        return error("文件不存在")
    return success(None, "更新成功")


@html_bp.delete("/<int:file_id>")
@login_required
def delete(file_id: int):
    ok = html_service.delete_html_file(file_id)
    if not ok:
        return error("文件不存在")
    return success(None, "删除成功")
