"""HTML 文件管理服务：扫描、增删改查。"""
from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, select, or_

from backend.database import engine
from backend.models import HtmlFile
from backend.services.scanner import scan_html_files
from backend.config import settings


def _build_url(relative_path: str) -> str:
    """根据相对路径生成访问 URL。"""
    # 使用相对路径作为 URL 路径，由 Flask 静态路由提供访问
    return f"/static/html/{relative_path}"


def sync_scan() -> dict:
    """执行扫描并同步到数据库。

    - 新文件 -> 新增记录
    - 已存在文件 -> 更新标题/大小/修改时间
    - 数据库中存在但磁盘已删除的文件 -> 标记（这里选择删除记录）
    返回新增/更新/删除数量。
    """
    files = scan_html_files()
    added = updated = removed = 0

    with Session(engine) as session:
        existing = {f.relative_path: f for f in session.exec(select(HtmlFile)).all()}
        scanned_paths = set()

        for info in files:
            scanned_paths.add(info["relative_path"])
            record = existing.get(info["relative_path"])
            if record:
                # 更新
                changed = False
                if record.title != info["title"]:
                    record.title = info["title"]
                    changed = True
                if record.file_size != info["file_size"]:
                    record.file_size = info["file_size"]
                    changed = True
                if record.last_modified != info["last_modified"]:
                    record.last_modified = info["last_modified"]
                    changed = True
                if record.absolute_path != info["absolute_path"]:
                    record.absolute_path = info["absolute_path"]
                    changed = True
                if changed:
                    record.updated_at = datetime.now()
                    session.add(record)
                    updated += 1
            else:
                # 新增
                new_file = HtmlFile(
                    filename=info["filename"],
                    relative_path=info["relative_path"],
                    absolute_path=info["absolute_path"],
                    url=_build_url(info["relative_path"]),
                    title=info["title"],
                    file_size=info["file_size"],
                    last_modified=info["last_modified"],
                )
                session.add(new_file)
                added += 1

        # 处理已删除的文件
        for rel_path, record in existing.items():
            if rel_path not in scanned_paths:
                session.delete(record)
                removed += 1

        session.commit()

    print(f"[html_service] 扫描完成: 新增 {added}, 更新 {updated}, 删除 {removed}")
    return {"added": added, "updated": updated, "removed": removed}


def list_html_files(keyword: Optional[str] = None) -> List[HtmlFile]:
    """查询 HTML 文件列表，支持关键词搜索（文件名/标题/路径）。"""
    with Session(engine) as session:
        stmt = select(HtmlFile)
        if keyword:
            kw = f"%{keyword}%"
            stmt = stmt.where(or_(
                HtmlFile.filename.like(kw),
                HtmlFile.title.like(kw),
                HtmlFile.relative_path.like(kw),
            ))
        stmt = stmt.order_by(HtmlFile.updated_at.desc())
        return session.exec(stmt).all()


def get_html_file(file_id: int) -> Optional[HtmlFile]:
    with Session(engine) as session:
        return session.get(HtmlFile, file_id)


def update_html_file(file_id: int, title: Optional[str] = None,
                     description: Optional[str] = None, url: Optional[str] = None) -> Optional[HtmlFile]:
    """更新 HTML 文件的标题/描述/URL。"""
    with Session(engine) as session:
        record = session.get(HtmlFile, file_id)
        if not record:
            return None
        if title is not None:
            record.title = title
        if description is not None:
            record.description = description
        if url is not None:
            record.url = url
        record.updated_at = datetime.now()
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


def delete_html_file(file_id: int) -> bool:
    """删除 HTML 文件记录（不删除磁盘文件）。"""
    with Session(engine) as session:
        record = session.get(HtmlFile, file_id)
        if not record:
            return False
        session.delete(record)
        session.commit()
        return True
