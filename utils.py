from translations import Translator
import sys
import os


def format_timedelta(delta, translator: Translator):
    """Formats a timedelta object into a human-readable string like '3 days' or '5 hours'."""
    seconds = int(delta.total_seconds())
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    if days > 0:
        return translator.get("duration_days", d=days)
    if hours > 0:
        return translator.get("duration_hours", h=hours)
    if minutes > 0:
        return translator.get("duration_minutes", m=minutes)
    return translator.get("duration_less_than_minute")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)