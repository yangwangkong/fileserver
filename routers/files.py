import mimetypes
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse

from config import settings
from routers.auth import get_csrf_token, is_authenticated, validate_csrf
from tpl import templates

router = APIRouter()

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".tiff"}
VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v", ".flv", ".wmv", ".rmvb"}
AUDIO_EXTS = {".mp3", ".flac", ".wav", ".ogg", ".m4a", ".aac", ".opus", ".wma"}
TEXT_EXTS = {
    ".txt", ".md", ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".htm",
    ".css", ".json", ".yaml", ".yml", ".xml", ".csv", ".log", ".sh",
    ".bat", ".ini", ".cfg", ".conf", ".toml", ".env", ".gitignore",
    ".c", ".cpp", ".h", ".hpp", ".java", ".go", ".rs", ".rb", ".php",
    ".swift", ".kt", ".sql", ".r", ".lua", ".vim", ".dockerfile",
}
ARCHIVE_EXTS = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tar.gz", ".tar.bz2"}

TEXT_PREVIEW_LIMIT = 1 * 1024 * 1024


def classify(ext: str) -> str:
    ext = ext.lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in VIDEO_EXTS:
        return "video"
    if ext in AUDIO_EXTS:
        return "audio"
    if ext == ".pdf":
        return "pdf"
    if ext in TEXT_EXTS:
        return "text"
    if ext in ARCHIVE_EXTS:
        return "archive"
    return "other"


def get_mount(name: str):
    for mount in settings.mounts:
        if mount.name == name:
            return mount
    return None


def safe_resolve(base: str, rel: str = "") -> Optional[Path]:
    base_path = Path(base).resolve()
    try:
        target = (base_path / rel).resolve() if rel else base_path
        target.relative_to(base_path)
        return target
    except (ValueError, OSError):
        return None


def format_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} B"
        size /= 1024
    return f"{size:.1f} PB"


def build_entry(path: Path, mount_base: Path, mount_name: str) -> dict:
    stat = path.stat()
    is_dir = path.is_dir()
    rel = path.relative_to(mount_base).as_posix()
    ext = path.suffix.lower()
    size = stat.st_size if not is_dir else 0
    return {
        "name": path.name,
        "is_dir": is_dir,
        "size": size,
        "size_str": format_size(size) if not is_dir else "-",
        "modified": stat.st_mtime,
        "ext": ext,
        "kind": "folder" if is_dir else classify(ext),
        "rel_path": rel,
        "browse_url": f"/browse/{mount_name}/{rel}" if is_dir else f"/preview/{mount_name}/{rel}",
        "download_url": f"/download/{mount_name}/{rel}" if not is_dir else None,
    }


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if not is_authenticated(request):
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "mounts": settings.mounts,
            "current_mount": None,
            "entries": [],
            "breadcrumbs": [],
            "current_path": "",
            "mount_name": "",
            "writable": False,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.get("/browse/{mount_name}", response_class=HTMLResponse)
@router.get("/browse/{mount_name}/{dir_path:path}", response_class=HTMLResponse)
async def browse(request: Request, mount_name: str, dir_path: str = ""):
    if not is_authenticated(request):
        return RedirectResponse(f"/login?next=/browse/{mount_name}/{dir_path}", status_code=302)

    mount = get_mount(mount_name)
    if not mount:
        raise HTTPException(404, "挂载点不存在")

    target = safe_resolve(mount.path, dir_path)
    if not target or not target.exists():
        raise HTTPException(404, "路径不存在")

    if target.is_file():
        return RedirectResponse(f"/preview/{mount_name}/{dir_path}", status_code=302)

    try:
        raw_entries = list(target.iterdir())
    except PermissionError as exc:
        raise HTTPException(403, "没有权限访问此目录") from exc

    mount_base = Path(mount.path).resolve()
    entries = []
    for item in raw_entries:
        try:
            entries.append(build_entry(item, mount_base, mount_name))
        except (OSError, ValueError):
            continue

    entries.sort(key=lambda entry: (not entry["is_dir"], entry["name"].lower()))

    breadcrumbs = [{"name": mount_name, "url": f"/browse/{mount_name}"}]
    parts = [part for part in dir_path.split("/") if part]
    for index, part in enumerate(parts):
        crumb_path = "/".join(parts[: index + 1])
        breadcrumbs.append({"name": part, "url": f"/browse/{mount_name}/{crumb_path}"})

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "mounts": settings.mounts,
            "current_mount": mount,
            "entries": entries,
            "breadcrumbs": breadcrumbs,
            "current_path": dir_path,
            "mount_name": mount_name,
            "writable": mount.writable,
            "upload_url": f"/upload/{mount_name}/{dir_path}" if dir_path else f"/upload/{mount_name}",
            "csrf_token": get_csrf_token(request),
        },
    )


@router.get("/preview/{mount_name}/{file_path:path}", response_class=HTMLResponse)
async def preview(request: Request, mount_name: str, file_path: str):
    if not is_authenticated(request):
        return RedirectResponse(f"/login?next=/preview/{mount_name}/{file_path}", status_code=302)

    mount = get_mount(mount_name)
    if not mount:
        raise HTTPException(404)

    target = safe_resolve(mount.path, file_path)
    if not target or not target.is_file():
        raise HTTPException(404, "文件不存在")

    ext = target.suffix.lower()
    kind = classify(ext)

    parts = [part for part in file_path.split("/") if part]
    parent_path = "/".join(parts[:-1])
    parent_url = f"/browse/{mount_name}/{parent_path}" if parent_path else f"/browse/{mount_name}"

    text_content = ""
    if kind == "text":
        try:
            size = target.stat().st_size
            if size <= TEXT_PREVIEW_LIMIT:
                text_content = target.read_text(encoding="utf-8", errors="replace")
            else:
                text_content = f"[文件过大（{format_size(size)}），无法预览，请下载后查看]"
        except Exception as exc:  # noqa: BLE001
            text_content = f"[读取失败: {exc}]"

    return templates.TemplateResponse(
        request,
        "preview.html",
        {
            "mounts": settings.mounts,
            "mount_name": mount_name,
            "file_path": file_path,
            "file_name": target.name,
            "file_size": format_size(target.stat().st_size),
            "kind": kind,
            "ext": ext,
            "text_content": text_content,
            "parent_url": parent_url,
            "download_url": f"/download/{mount_name}/{file_path}",
            "raw_url": f"/raw/{mount_name}/{file_path}",
            "csrf_token": get_csrf_token(request),
        },
    )


@router.get("/download/{mount_name}/{file_path:path}")
async def download(request: Request, mount_name: str, file_path: str):
    if not is_authenticated(request):
        raise HTTPException(401, "请先登录")

    mount = get_mount(mount_name)
    if not mount:
        raise HTTPException(404)

    target = safe_resolve(mount.path, file_path)
    if not target or not target.is_file():
        raise HTTPException(404, "文件不存在")

    return FileResponse(path=target, filename=target.name, media_type="application/octet-stream")


@router.get("/raw/{mount_name}/{file_path:path}")
async def raw(request: Request, mount_name: str, file_path: str):
    if not is_authenticated(request):
        raise HTTPException(401)

    mount = get_mount(mount_name)
    if not mount:
        raise HTTPException(404)

    target = safe_resolve(mount.path, file_path)
    if not target or not target.is_file():
        raise HTTPException(404)

    mime, _ = mimetypes.guess_type(str(target))
    return FileResponse(path=target, media_type=mime or "application/octet-stream")


@router.post("/upload/{mount_name}")
@router.post("/upload/{mount_name}/{dir_path:path}")
async def upload(request: Request, mount_name: str, dir_path: str = "", file: UploadFile = File(...)):
    if not is_authenticated(request):
        raise HTTPException(401, "请先登录")
    validate_csrf(request)

    mount = get_mount(mount_name)
    if not mount:
        raise HTTPException(404, "挂载点不存在")
    if not mount.writable:
        raise HTTPException(403, "该挂载点为只读")

    target_dir = safe_resolve(mount.path, dir_path)
    if not target_dir or not target_dir.is_dir():
        raise HTTPException(404, "目标目录不存在")

    filename = Path(file.filename).name if file.filename else ""
    if not filename:
        raise HTTPException(400, "文件名无效")

    dest = target_dir / filename
    content = await file.read()
    dest.write_bytes(content)

    return JSONResponse({"success": True, "filename": filename, "size": len(content)})


@router.delete("/delete/{mount_name}/{file_path:path}")
async def delete_file(request: Request, mount_name: str, file_path: str):
    if not is_authenticated(request):
        raise HTTPException(401)
    validate_csrf(request)

    mount = get_mount(mount_name)
    if not mount:
        raise HTTPException(404)
    if not mount.writable:
        raise HTTPException(403, "该挂载点为只读")

    target = safe_resolve(mount.path, file_path)
    if not target or not target.exists():
        raise HTTPException(404)
    if target == Path(mount.path).resolve():
        raise HTTPException(400, "不能删除挂载根目录")

    if target.is_file():
        target.unlink()
    elif target.is_dir():
        shutil.rmtree(target)

    return JSONResponse({"success": True})
