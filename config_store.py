import os
import streamlit as st


def get_secret(key, default=""):
    """Read Streamlit secrets safely, then fall back to environment variables.

    This prevents a missing secrets.toml file from crashing the app on hosting
    platforms such as Hugging Face Spaces.
    """
    try:
        value = st.secrets.get(key, None)
        if value not in (None, ""):
            return value
    except (FileNotFoundError, RuntimeError, AttributeError, KeyError, TypeError):
        pass
    return os.getenv(key, default)


def _default_config():
    return {
        "event_name": "Event Gallery",
        "provider": "drive",
        "folder_url": "",
        "threshold": 0.40,
        "enabled": False,
    }


def load_config():
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_KEY")

    if not url or not key:
        return _default_config()

    try:
        from supabase import create_client
        client = create_client(url, key)
        response = (
            client.table("event_config")
            .select("*")
            .eq("id", 1)
            .limit(1)
            .execute()
        )
        if response.data:
            row = response.data[0]
            cfg = _default_config()
            cfg.update({
                "event_name": row.get("event_name", cfg["event_name"]),
                "provider": row.get("provider", cfg["provider"]),
                "folder_url": row.get("folder_url", cfg["folder_url"]),
                "threshold": row.get("threshold", cfg["threshold"]),
                "enabled": row.get("enabled", cfg["enabled"]),
            })
            return cfg
    except Exception as exc:
        try:
            st.warning(f"Unable to load event configuration from Supabase: {exc}")
        except Exception:
            pass

    return _default_config()


def save_config(cfg):
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError(
            "Supabase credentials are missing. Add SUPABASE_URL and "
            "SUPABASE_KEY in the hosting platform's Secrets settings, or "
            "configure them in Streamlit secrets."
        )

    from supabase import create_client
    client = create_client(url, key)
    payload = {
        "id": 1,
        "event_name": cfg.get("event_name", "Event Gallery"),
        "provider": cfg.get("provider", "drive"),
        "folder_url": cfg.get("folder_url", ""),
        "threshold": cfg.get("threshold", 0.40),
        "enabled": cfg.get("enabled", False),
    }
    client.table("event_config").upsert(payload).execute()
