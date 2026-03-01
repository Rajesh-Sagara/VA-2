"""
File Validator – validates uploaded files by MIME type and extension.
Provides a clean category label for each file type the system supports.
Uses python-magic when available; falls back to extension-based detection.
"""

import os
import mimetypes

# ──────────────────────────────────────────────────────────────────────────────
# Extension → category map (fallback when python-magic is unavailable)
# ──────────────────────────────────────────────────────────────────────────────
_EXT_CATEGORY = {
    # Documents
    ".pdf":  "document",
    ".doc":  "document",
    ".docx": "document",
    ".txt":  "document",
    ".rtf":  "document",
    ".odt":  "document",
    # Images
    ".jpg":  "image",
    ".jpeg": "image",
    ".png":  "image",
    ".gif":  "image",
    ".bmp":  "image",
    ".webp": "image",
    ".tiff": "image",
    ".svg":  "image",
    # Videos
    ".mp4":  "video",
    ".avi":  "video",
    ".mov":  "video",
    ".mkv":  "video",
    ".wmv":  "video",
    ".flv":  "video",
    ".webm": "video",
    # Spreadsheets
    ".xlsx": "spreadsheet",
    ".xls":  "spreadsheet",
    ".csv":  "spreadsheet",
    ".ods":  "spreadsheet",
    # Presentations
    ".ppt":  "presentation",
    ".pptx": "presentation",
}

_MIME_CATEGORY = {
    "application/pdf":                     "document",
    "application/msword":                  "document",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
    "text/plain":                          "document",
    "image/jpeg":                          "image",
    "image/png":                           "image",
    "image/gif":                           "image",
    "image/bmp":                           "image",
    "image/webp":                          "image",
    "image/tiff":                          "image",
    "image/svg+xml":                       "image",
    "video/mp4":                           "video",
    "video/x-msvideo":                     "video",
    "video/quicktime":                     "video",
    "video/x-matroska":                    "video",
    "video/webm":                          "video",
    "application/vnd.ms-excel":            "spreadsheet",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "spreadsheet",
    "text/csv":                            "spreadsheet",
}

# Try to import python-magic (optional dependency)
try:
    import magic as _magic
    _MAGIC_AVAILABLE = True
except ImportError:
    _MAGIC_AVAILABLE = False


def _get_mime_via_magic(content: bytes) -> str:
    """Use python-magic to detect MIME from raw bytes."""
    try:
        return _magic.from_buffer(content, mime=True)
    except Exception:
        return "application/octet-stream"


def _get_mime_via_mimetypes(filename: str) -> str:
    """Use stdlib mimetypes as fallback."""
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"


def validate_file(content: bytes, filename: str) -> dict:
    """
    Validate an uploaded file and return metadata.

    Returns:
        {
            "mime_type": str,
            "category": str,   # document / image / video / spreadsheet / other
            "extension": str,
            "size_bytes": int,
            "valid": bool,
            "message": str
        }
    """
    ext = os.path.splitext(filename)[-1].lower()
    size = len(content)

    # Determine MIME type
    if _MAGIC_AVAILABLE and content:
        mime_type = _get_mime_via_magic(content)
    else:
        mime_type = _get_mime_via_mimetypes(filename)

    # Determine category
    category = _MIME_CATEGORY.get(mime_type) or _EXT_CATEGORY.get(ext, "other")

    # Basic size guard: reject empty files
    if size == 0:
        return {
            "mime_type": mime_type,
            "category": category,
            "extension": ext,
            "size_bytes": size,
            "valid": False,
            "message": "File is empty",
        }

    return {
        "mime_type": mime_type,
        "category": category,
        "extension": ext,
        "size_bytes": size,
        "valid": True,
        "message": "OK",
    }
