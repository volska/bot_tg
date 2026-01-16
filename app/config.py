import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    bot_token: str
    public_base_url: str
    database_url: str

    terms_url: str
    privacy_url: str
    terms_version: str
    privacy_version: str

    group_password: str
    group_invite_link: str

    hold_ttl_min: int

def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    public_base_url = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")
    database_url = os.getenv("DATABASE_URL", "").strip()

    terms_url = os.getenv("TERMS_URL", "").strip()
    privacy_url = os.getenv("PRIVACY_URL", "").strip()
    terms_version = os.getenv("TERMS_VERSION", "").strip()
    privacy_version = os.getenv("PRIVACY_VERSION", "").strip()

    group_password = os.getenv("GROUP_PASSWORD", "").strip()
    group_invite_link = os.getenv("GROUP_INVITE_LINK", "").strip()

    hold_ttl_min = int(os.getenv("HOLD_TTL_MIN", "15").strip())

    missing = []
    if not bot_token: missing.append("BOT_TOKEN")
    if not public_base_url: missing.append("PUBLIC_BASE_URL")
    if not database_url: missing.append("DATABASE_URL")
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

    return Config(
        bot_token=bot_token,
        public_base_url=public_base_url,
        database_url=database_url,
        terms_url=terms_url,
        privacy_url=privacy_url,
        terms_version=terms_version or "unknown",
        privacy_version=privacy_version or "unknown",
        group_password=group_password,
        group_invite_link=group_invite_link,
        hold_ttl_min=hold_ttl_min,
    )