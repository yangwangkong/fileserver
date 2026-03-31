from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from config import settings, verify_password
from tpl import templates

router = APIRouter()


def is_authenticated(request: Request) -> bool:
    return request.session.get("authenticated", False)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/"):
    if is_authenticated(request):
        return RedirectResponse(next, status_code=302)
    return templates.TemplateResponse(request, "login.html", {"next": next, "error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form(default="/"),
):
    if username == settings.username and verify_password(password, settings.password_hash, settings.legacy_password):
        request.session["authenticated"] = True
        return RedirectResponse(next or "/", status_code=302)
    return templates.TemplateResponse(
        request,
        "login.html",
        {"next": next, "error": "用户名或密码错误"},
        status_code=401,
    )


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)
