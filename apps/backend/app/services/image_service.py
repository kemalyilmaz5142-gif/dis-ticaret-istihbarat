import hashlib
import json
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.schemas.search import ImageUploadResponse

try:
    from PIL import Image
except ImportError:  # pragma: no cover - fallback when Pillow is not installed yet.
    Image = None


STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage"
IMAGE_DIR = STORAGE_DIR / "product-images"
IMAGE_INDEX = STORAGE_DIR / "product-images.json"


def save_product_image(file: UploadFile) -> ImageUploadResponse:
    image_id = str(uuid4())
    extension = _extension_from_name(file.filename or "")
    image_path = IMAGE_DIR / f"{image_id}{extension}"
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    content = file.file.read()
    image_path.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    analysis = _analyze_image(content)

    response = ImageUploadResponse(
        image_id=image_id,
        filename=file.filename or image_path.name,
        content_type=file.content_type,
        size_bytes=len(content),
        sha256=digest,
        width=analysis.get("width"),
        height=analysis.get("height"),
        image_format=analysis.get("image_format"),
        average_color=analysis.get("average_color"),
        visual_signature=analysis.get("visual_signature") or digest[:16],
    )
    _add_index(response, image_path.name)
    return response


def get_image_metadata(image_id: str) -> dict | None:
    for row in _read_index():
        if row.get("image_id") == image_id:
            return row
    return None


def _add_index(response: ImageUploadResponse, stored_name: str) -> None:
    rows = _read_index()
    row = response.model_dump()
    row["stored_name"] = stored_name
    rows.insert(0, row)
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_INDEX.write_text(json.dumps(rows[:200], ensure_ascii=True, indent=2), encoding="utf-8")


def _read_index() -> list[dict]:
    if not IMAGE_INDEX.exists():
        return []
    try:
        data = json.loads(IMAGE_INDEX.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]


def _extension_from_name(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}:
        return suffix
    return ".bin"


def _analyze_image(content: bytes) -> dict:
    if Image is None:
        return {}
    try:
        with Image.open(BytesIO(content)) as image:
            rgb_image = image.convert("RGB")
            small = rgb_image.resize((1, 1))
            red, green, blue = small.getpixel((0, 0))
            average_color = f"#{red:02x}{green:02x}{blue:02x}"
            signature_source = f"{image.width}x{image.height}:{image.format}:{average_color}".encode("utf-8")
            return {
                "width": image.width,
                "height": image.height,
                "image_format": image.format,
                "average_color": average_color,
                "visual_signature": hashlib.sha256(signature_source).hexdigest()[:16],
            }
    except Exception:
        return {}
