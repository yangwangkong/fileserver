import hmac
import secrets
from urllib.parse import urlsplit

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from config import settings, verify_password
from tpl import templates

router = APIRouter()


CSRF_SESSION_KEY = "csrf_token"


def is_authenticated(request: Request) -> bool:
    return request.session.get("authenticated", False)


def get_csrf_token(request: Request) -> str:
    token = request.session.get(CSRF_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        request.session[CSRF_SESSION_KEY] = token
    return token


def validate_csrf(request: Request, supplied_token: str | None = None) -> None:
    expected = request.session.get(CSRF_SESSION_KEY, "")
    actual = supplied_token or request.headers.get("x-csrf-token", "")
    if not expected or not actual or not hmac.compare_digest(expected, actual):
        raise HTTPException(403, "Invalid CSRF token")


def sanitize_next(next_path: str | None) -> str:
    if not next_path:
        return "/"

    parsed = urlsplit(next_path)
    if parsed.scheme or parsed.netloc:
        return "/"
    if not next_path.startswith("/") or next_path.startswith("//"):
        return "/"
    return next_path


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/"):
    safe_next = sanitize_next(next)
    if is_authenticated(request):
        return RedirectResponse(safe_next, status_code=302)
    return templates.TemplateResponse(
        request,
        "login.html",
        {"next": safe_next, "error": None, "csrf_token": get_csrf_token(request)},
    )


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form(default="/"),
    csrf_token: str = Form(...),
):
    validate_csrf(request, csrf_token)
    safe_next = sanitize_next(next)
    if username == settings.username and verify_password(password, settings.password_hash, settings.legacy_password):
        request.session.clear()
        request.session["authenticated"] = True
        request.session[CSRF_SESSION_KEY] = secrets.token_urlsafe(32)
        return RedirectResponse(safe_next, status_code=302)
    return templates.TemplateResponse(
        request,
        "login.html",
        {"next": safe_next, "error": "用户名或密码错误", "csrf_token": get_csrf_token(request)},
        status_code=401,
    )


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)
