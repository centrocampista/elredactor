from pathlib import Path
from app.config import settings

UPLOAD_DIR = Path(settings.upload_dir_name)
MAX_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_TYPES = {
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}
