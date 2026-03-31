"""Shared Jinja2Templates instance with custom filters."""
import sys
from datetime import datetime
from pathlib import Path

from fastapi.templating import Jinja2Templates

BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _datetimeformat(ts: float) -> str:
    return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")


templates.env.filters["datetimeformat"] = _datetimeformat
