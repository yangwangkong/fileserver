from pathlib import Path
from urllib.parse import urlencode

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from config import MountConfig, reload_settings, save_mounts, save_password, settings, verify_password
from routers.auth import get_csrf_token, is_authenticated, validate_csrf
from tpl import templates

router = APIRouter()


def _redirect(message: str = "", error: str = "") -> RedirectResponse:
    params = {}
    if message:
        params["message"] = message
    if error:
        params["error"] = error
    suffix = f"?{urlencode(params)}" if params else ""
    return RedirectResponse(f"/settings/mounts{suffix}", status_code=302)


@router.get("/settings/mounts", response_class=HTMLResponse)
async def mount_settings_page(request: Request, message: str = "", error: str = ""):
    if not is_authenticated(request):
        return RedirectResponse("/login?next=/settings/mounts", status_code=302)

    return templates.TemplateResponse(
        request,
        "settings.html",
        {
            "mounts": settings.mounts,
            "current_mount": None,
            "entries": [],
            "breadcrumbs": [],
            "current_path": "",
            "mount_name": "",
            "writable": False,
            "message": message,
            "error": error,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/settings/mounts")
async def save_mount(
    request: Request,
    original_name: str = Form(default=""),
    name: str = Form(...),
    path: str = Form(...),
    writable: bool = Form(default=False),
    csrf_token: str = Form(...),
):
    if not is_authenticated(request):
        raise HTTPException(401, "请先登录")
    validate_csrf(request, csrf_token)

    mount_name = name.strip()
    mount_path = path.strip()
    if not mount_name:
        return _redirect(error="挂载名称不能为空")
    if not mount_path:
        return _redirect(error="挂载路径不能为空")

    resolved_path = Path(mount_path).expanduser()
    try:
        resolved_path = resolved_path.resolve()
    except OSError:
        return _redirect(error="挂载路径无效")

    if not resolved_path.exists() or not resolved_path.is_dir():
        return _redirect(error="挂载路径必须是已存在的目录")

    mounts = list(settings.mounts)
    normalized_original = original_name.strip()

    for mount in mounts:
        if mount.name == mount_name and mount.name != normalized_original:
            return _redirect(error="挂载名称已存在")

    updated_mount = MountConfig(name=mount_name, path=str(resolved_path), writable=writable)
    replaced = False
    for index, mount in enumerate(mounts):
        if mount.name == normalized_original:
            mounts[index] = updated_mount
            replaced = True
            break

    if not replaced:
        mounts.append(updated_mount)

    save_mounts(mounts)
    reload_settings()
    return _redirect(message="挂载配置已保存")


@router.post("/settings/mounts/delete")
async def delete_mount(request: Request, name: str = Form(...), csrf_token: str = Form(...)):
    if not is_authenticated(request):
        raise HTTPException(401, "请先登录")
    validate_csrf(request, csrf_token)

    target_name = name.strip()
    mounts = [mount for mount in settings.mounts if mount.name != target_name]
    if len(mounts) == len(settings.mounts):
        return _redirect(error="未找到要删除的挂载点")

    save_mounts(mounts)
    reload_settings()
    return _redirect(message="挂载点已删除")


@router.post("/settings/password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(...),
):
    if not is_authenticated(request):
        raise HTTPException(401, "请先登录")
    validate_csrf(request, csrf_token)

    if not verify_password(current_password, settings.password_hash, settings.legacy_password):
        return _redirect(error="当前密码不正确")

    new_password = new_password.strip()
    confirm_password = confirm_password.strip()

    if len(new_password) < 8:
        return _redirect(error="新密码至少需要 8 位")
    if new_password != confirm_password:
        return _redirect(error="两次输入的新密码不一致")
    if verify_password(new_password, settings.password_hash, settings.legacy_password):
        return _redirect(error="新密码不能与当前密码相同")

    save_password(new_password)
    reload_settings()
    request.session.clear()
    return RedirectResponse("/login?next=/settings/mounts", status_code=302)
