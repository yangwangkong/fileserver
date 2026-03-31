import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

import pystray
import uvicorn
from fastapi import FastAPI
from PIL import Image, ImageDraw
from starlette.middleware.sessions import SessionMiddleware

# Ensure project root is on sys.path when running as a script
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from routers import admin, auth, files

app = FastAPI(title="FileServer", docs_url=None, redoc_url=None)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    max_age=86400 * 7,
    same_site="lax",
    https_only=False,
)

app.include_router(auth.router)
app.include_router(files.router)
app.include_router(admin.router)

LOCAL_URL = f"http://127.0.0.1:{settings.port}"
LAN_URL = f"http://<LAN-IP>:{settings.port}"
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
RUNTIME_LOG = APP_DIR / "fileserver_runtime.log"

_server: uvicorn.Server | None = None
_server_thread: threading.Thread | None = None
_shutdown_event = threading.Event()


def create_tray_icon() -> Image.Image:
    size = 64
    image = Image.new("RGBA", (size, size), (24, 32, 48, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, 56, 56), radius=14, fill=(37, 99, 235, 255))
    draw.rectangle((20, 20, 44, 28), fill=(255, 255, 255, 230))
    draw.rectangle((20, 34, 44, 42), fill=(191, 219, 254, 255))
    draw.rectangle((20, 46, 36, 50), fill=(191, 219, 254, 255))
    return image


def wait_for_server(host: str, port: int, timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline and not _shutdown_event.is_set():
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.25)
    return False


def open_browser_when_ready() -> None:
    if wait_for_server("127.0.0.1", settings.port):
        write_runtime_log("Server is ready, opening browser")
        webbrowser.open(LOCAL_URL, new=2)
    else:
        write_runtime_log("Server did not become ready before timeout")


def write_runtime_log(message: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(RUNTIME_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def run_server() -> None:
    global _server
    try:
        config = uvicorn.Config(
            app,
            host=settings.host,
            port=settings.port,
            reload=False,
            log_level="info",
            log_config=None,
            access_log=False,
        )
        _server = uvicorn.Server(config)
        _server.run()
    except Exception as exc:  # noqa: BLE001
        write_runtime_log(f"Server failed to start: {exc!r}")
    finally:
        _shutdown_event.set()


def stop_server() -> None:
    _shutdown_event.set()
    if _server is not None:
        _server.should_exit = True
    write_runtime_log("Shutdown requested")


def on_open(_: pystray.Icon, __: pystray.MenuItem) -> None:
    webbrowser.open(LOCAL_URL, new=2)


def on_exit(icon: pystray.Icon, _: pystray.MenuItem) -> None:
    stop_server()
    icon.stop()


def run_tray() -> None:
    icon = pystray.Icon(
        "fileserver",
        create_tray_icon(),
        "FileServer",
        menu=pystray.Menu(
            pystray.MenuItem("Open FileServer", on_open, default=True),
            pystray.MenuItem(f"Address: {LOCAL_URL}", on_open),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", on_exit),
        ),
    )
    icon.run()


def main() -> None:
    global _server_thread

    write_runtime_log("FileServer starting")
    write_runtime_log(f"Local URL: {LOCAL_URL}")
    write_runtime_log(f"LAN URL: {LAN_URL}")

    _server_thread = threading.Thread(target=run_server, name="fileserver-uvicorn", daemon=True)
    _server_thread.start()

    threading.Thread(target=open_browser_when_ready, name="fileserver-browser", daemon=True).start()

    try:
        run_tray()
    finally:
        stop_server()
        if _server_thread is not None:
            _server_thread.join(timeout=10)


if __name__ == "__main__":
    main()
