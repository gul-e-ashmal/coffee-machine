import json
import os
import tempfile


def load_json(path, default):
    """Read a JSON file. If it doesn't exist, create it with `default`."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if not os.path.exists(path):
        save_json(path, default)
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: {os.path.basename(path)} is corrupted. Using empty data.")
        return default


def save_json(path, data):
    """Write JSON safely: write to a temp file first, then replace the real file."""
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, path)  # atomic replace
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise