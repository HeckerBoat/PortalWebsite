"""HTML 文件扫描服务：扫描目录，提取信息。"""
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from backend.config import BASE_DIR

# 扫描时排除的目录
EXCLUDE_DIRS = {"node_modules", "dist", ".git", ".vite", "__pycache__", ".venv", "backend"}

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def _extract_title(content: str) -> str:
    """从 HTML 内容中提取 <title>。"""
    m = TITLE_RE.search(content)
    if m:
        return m.group(1).strip()[:255]
    return ""


def get_scan_root() -> Path:
    """获取扫描根目录（绝对路径）。"""
    from backend.config import settings
    p = Path(settings.HTML_SCAN_DIR)
    if not p.is_absolute():
        p = BASE_DIR / p
    return p


def scan_html_files() -> List[Dict]:
    """扫描 HTML_SCAN_DIR 下所有 .html 文件，返回文件信息列表。

    排除 node_modules、dist 等构建目录。
    """
    root = get_scan_root()
    results: List[Dict] = []
    if not root.exists():
        print(f"[scanner] 扫描目录不存在: {root}")
        return results

    for path in root.rglob("*.html"):
        # 排除指定目录
        parts = set(path.parts)
        if parts & EXCLUDE_DIRS:
            continue
        # 排除扫描根目录下的 index.html（Vite 入口模板，不属于被管理的 HTML）
        try:
            if path.parent == root and path.name == "index.html":
                continue
        except ValueError:
            pass

        try:
            stat = path.stat()
            content = path.read_text(encoding="utf-8", errors="ignore")
            title = _extract_title(content)
            rel = path.relative_to(root)
            results.append({
                "filename": path.name,
                "relative_path": str(rel).replace("\\", "/"),
                "absolute_path": str(path),
                "title": title,
                "file_size": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime),
            })
        except Exception as e:
            print(f"[scanner] 读取文件失败 {path}: {e}")
    return results
