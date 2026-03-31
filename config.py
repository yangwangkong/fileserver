import os
import secrets
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional
import hashlib
import hmac

import yaml


@dataclass
class MountConfig:
    name: str
    path: str
    writable: bool = False


@dataclass
class Settings:
    host: str
    port: int
    secret_key: str
    username: str
    password_hash: str = ""
    legacy_password: Optional[str] = None
    mounts: List[MountConfig] = field(default_factory=list)


BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "config.yaml"
RUNTIME_CONFIG_PATH = APP_DIR / "runtime_config.yaml"
ENV_SECRET_KEY = "FILESERVER_SECRET_KEY"


def _ensure_app_dir() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_runtime_config() -> dict:
    return _read_yaml(RUNTIME_CONFIG_PATH)



def _save_runtime_config(data: dict) -> None:
    _ensure_app_dir()
    with open(RUNTIME_CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def _default_config_path() -> Path:
    app_config = CONFIG_PATH
    if app_config.exists():
        return app_config

    bundled_config = BASE_DIR / "config.yaml"
    if bundled_config.exists():
        return bundled_config

    raise FileNotFoundError(f"config.yaml not found at {app_config} or {bundled_config}")


def _is_secure_secret(secret: str) -> bool:
    lowered = (secret or "").strip().lower()
    return bool(secret) and len(secret) >= 32 and "placeholder" not in lowered


def _get_effective_secret_key(base_data: dict, runtime_data: dict) -> str:
    env_secret = os.getenv(ENV_SECRET_KEY, "")
    if _is_secure_secret(env_secret):
        return env_secret

    runtime_server = runtime_data.setdefault("server", {})
    runtime_secret = runtime_server.get("secret_key", "")
    if _is_secure_secret(runtime_secret):
        return runtime_secret

    base_secret = base_data["server"].get("secret_key", "")
    if _is_secure_secret(base_secret):
        return base_secret

    generated_secret = secrets.token_urlsafe(48)
    runtime_server["secret_key"] = generated_secret
    _save_runtime_config(runtime_data)
    return generated_secret


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    iterations = 100_000
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${derived.hex()}"


def verify_password(candidate: str, password_hash: str = "", legacy_password: Optional[str] = None) -> bool:
    if password_hash:
        try:
            algorithm, iterations_text, salt, expected = password_hash.split("$", 3)
            if algorithm != "pbkdf2_sha256":
                return False
            actual = hashlib.pbkdf2_hmac(
                "sha256",
                candidate.encode("utf-8"),
                salt.encode("utf-8"),
                int(iterations_text),
            ).hex()
            return hmac.compare_digest(actual, expected)
        except (TypeError, ValueError):
            return False

    if legacy_password is None:
        return False
    return hmac.compare_digest(candidate, legacy_password)


def load_config() -> Settings:
    base_data = _read_yaml(_default_config_path())
    runtime_data = _load_runtime_config()

    mounts_data = runtime_data.get("mounts")
    if mounts_data is None:
        mounts_data = base_data.get("mounts", [])

    runtime_auth = runtime_data.get("auth", {})
    mounts = [MountConfig(**m) for m in mounts_data]

    return Settings(
        host=base_data["server"]["host"],
        port=base_data["server"]["port"],
        secret_key=_get_effective_secret_key(base_data, runtime_data),
        username=base_data["auth"]["username"],
        password_hash=runtime_auth.get("password_hash", base_data["auth"].get("password_hash", "")),
        legacy_password=runtime_auth.get("password", base_data["auth"].get("password")),
        mounts=mounts,
    )


def save_mounts(mounts: List[MountConfig]) -> None:
    runtime_data = _load_runtime_config()
    runtime_data["mounts"] = [asdict(mount) for mount in mounts]
    _save_runtime_config(runtime_data)


def save_password(password: str) -> None:
    runtime_data = _load_runtime_config()
    auth_data = runtime_data.get("auth", {})
    auth_data.pop("password", None)
    auth_data["password_hash"] = hash_password(password)
    runtime_data["auth"] = auth_data
    _save_runtime_config(runtime_data)


def reload_settings() -> Settings:
    fresh = load_config()
    settings.host = fresh.host
    settings.port = fresh.port
    settings.secret_key = fresh.secret_key
    settings.username = fresh.username
    settings.password_hash = fresh.password_hash
    settings.legacy_password = fresh.legacy_password
    settings.mounts = fresh.mounts
    return settings


settings = load_config()
