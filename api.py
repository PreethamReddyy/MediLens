"""
api.py

Lightweight FastAPI backend for MediLens.AI deployment.

IMPORTANT:
This cloud API intentionally does NOT import medeye_ocr_engine.py because that
module loads EasyOCR/PyTorch and exceeds Render Free's memory limit.
OCR is delegated to OCR.space instead.
"""

import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ocr_space_engine import MediLensCloudOCR

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "api_uploads"
AUDIO_DIR = BASE_DIR / "api_audio"
UPLOAD_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

app = FastAPI(title="MediLens.AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

engine = MediLensCloudOCR()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
}


@app.get("/")
def root():
    return {
        "service": "MediLens.AI",
        "status": "running",
        "ocr": "OCR.space",
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "MediLens.AI",
        "ocr_engine": "OCR.space",
    }


@app.post("/api/scan")
async def scan_medicine(
    image: UploadFile = File(...),
    language: str = Form("en"),
):
    if language not in {"en", "te", "hi"}:
        raise HTTPException(status_code=400, detail="Language must be en, te, or hi.")

    extension = Path(image.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported image format.")

    if image.content_type and image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image content type.")

    file_id = uuid.uuid4().hex
    image_path = UPLOAD_DIR / f"{file_id}{extension}"

    try:
        with image_path.open("wb") as output:
            shutil.copyfileobj(image.file, output)

        # OCR.space free API has a 1 MB file limit. Reject oversized uploads
        # instead of sending a request that will definitely fail.
        if image_path.stat().st_size > 1_000_000:
            raise HTTPException(
                status_code=413,
                detail="Image is larger than 1 MB. Please upload a smaller/compressed image.",
            )

        result = engine.process_image(
            str(image_path),
            voice_language=language,
        )

        for medicine in result.get("medicines", []):
            audio_path = medicine.pop("audio_path", None)
            if not audio_path:
                medicine["audio_url"] = None
                continue

            source = Path(audio_path)
            if not source.exists():
                medicine["audio_url"] = None
                continue

            destination_name = f"{uuid.uuid4().hex}_{source.name}"
            destination = AUDIO_DIR / destination_name
            shutil.copy2(source, destination)
            medicine["audio_url"] = f"/audio/{destination_name}"

        return result

    except HTTPException:
        raise
    except Exception as exc:
        print(f"Scan failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        try:
            image_path.unlink(missing_ok=True)
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
