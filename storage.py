"""Small helper functions for reading/writing the JSON data file."""

import json
from pathlib import Path


def read_json(file_path: Path, fallback):
    if not file_path.exists():
        return fallback
    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return fallback


def write_json(file_path: Path, data):
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
