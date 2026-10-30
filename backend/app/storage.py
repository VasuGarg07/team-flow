from pathlib import Path

from app.config import app_settings

def file_path(stored_name: str) -> Path:
    folder = Path(app_settings.UPLOAD_DIR)
    folder.mkdir(parents=True, exist_ok=True)
    return folder / stored_name

def save_file(stored_name: str, content: bytes) -> None:
    file_path(stored_name).write_bytes(content)

def delete_file(stored_name: str) -> None:
    file_path(stored_name).unlink(missing_ok=True)