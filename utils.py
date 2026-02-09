from translations import Translator
import sys
import os
import re


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


def get_latest_release_notes():
    """
    Reads WHATS_NEW.md and extracts the notes for the latest version.
    """
    try:
        notes_path = resource_path("WHATS_NEW.md")
        if not os.path.exists(notes_path):
            return "No release notes found."

        with open(notes_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find the first version header (## Version X.X.X)
        match = re.search(r"## Version (\d+\.\d+\.\d+)", content)
        if not match:
            return content  # Fallback: return everything if no version header found

        current_version_header = match.group(0)
        start_index = content.find(current_version_header)
        
        # Find the next version header to determine the end of the current section
        next_header_match = re.search(r"## Version \d+\.\d+\.\d+", content[start_index + len(current_version_header):])
        
        if next_header_match:
            end_index = start_index + len(current_version_header) + next_header_match.start()
            return content[start_index:end_index].strip()
        else:
            return content[start_index:].strip()

    except Exception as e:
        return f"Error reading release notes: {e}"