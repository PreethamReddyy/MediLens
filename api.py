from pathlib import Path
import shutil
import uuid

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from medeye_ocr_engine import MediLensOCR


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "api_uploads"
AUDIO_DIR = BASE_DIR / "api_audio"

UPLOAD_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="MediLens.AI API",
    description="Backend API for MediLens.AI medicine recognition",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# AUDIO FILE SERVER
# ============================================================

app.mount(
    "/audio",
    StaticFiles(directory=str(AUDIO_DIR)),
    name="audio",
)


# ============================================================
# MEDILENS ENGINE
# ============================================================

print()
print("=" * 60)
print("          MEDILENS.AI BACKEND")
print("=" * 60)
print("Initializing OCR engine...")
print()

engine = MediLensOCR()

print()
print("MediLens OCR engine ready.")
print("=" * 60)
print()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():
    return {
        "name": "MediLens.AI",
        "status": "online",
        "message": "MediLens.AI backend is running.",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "MediLens.AI",
        "ocr_engine": "ready",
    }


# ============================================================
# HELPERS
# ============================================================

def allowed_image(filename: str, content_type: str | None) -> bool:
    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
    }

    extension = Path(filename).suffix.lower()

    if extension not in allowed_extensions:
        return False

    if content_type and not content_type.startswith("image/"):
        return False

    return True


def prepare_audio_file(audio_path: str | None) -> str | None:
    """
    Copies the generated MediLens audio file into the API's
    public audio directory and returns a browser-friendly URL.
    """

    if not audio_path:
        return None

    source = Path(audio_path)

    if not source.exists():
        return None

    unique_name = f"{uuid.uuid4().hex}_{source.name}"
    destination = AUDIO_DIR / unique_name

    try:
        shutil.copy2(source, destination)
    except Exception as exc:
        print(f"Audio copy warning: {exc}")
        return None

    return f"/audio/{destination.name}"


# ============================================================
# MEDICINE SCAN ENDPOINT
# ============================================================

@app.post("/api/scan")
async def scan_medicine(
    image: UploadFile = File(...),
    language: str = Form("en"),
):
    """
    Receives an image from the React frontend,
    sends it through the existing MediLens OCR pipeline,
    generates multilingual audio,
    and returns the medicine information as JSON.
    """

    # --------------------------------------------------------
    # Validate language
    # --------------------------------------------------------

    language = language.lower().strip()

    if language not in {"en", "te", "hi"}:
        language = "en"

    # --------------------------------------------------------
    # Validate uploaded image
    # --------------------------------------------------------

    filename = image.filename or "medicine.jpg"

    if not allowed_image(filename, image.content_type):
        raise HTTPException(
            status_code=400,
            detail=(
                "Please upload a valid medicine image "
                "(JPG, JPEG, PNG, WEBP, or BMP)."
            ),
        )

    # --------------------------------------------------------
    # Create temporary upload filename
    # --------------------------------------------------------

    extension = Path(filename).suffix.lower()

    if not extension:
        extension = ".jpg"

    temporary_filename = f"{uuid.uuid4().hex}{extension}"
    image_path = UPLOAD_DIR / temporary_filename

    # --------------------------------------------------------
    # Save uploaded image
    # --------------------------------------------------------

    try:
        with image_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not save uploaded image: {exc}",
        )

    # --------------------------------------------------------
    # Run MediLens OCR pipeline
    # --------------------------------------------------------

    try:
        result = engine.process_image(
            str(image_path),
            voice_language=language,
            play_voice=False,
        )

    except Exception as exc:
        print()
        print("MediLens processing error:")
        print(exc)
        print()

        try:
            image_path.unlink(missing_ok=True)
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail=(
                "MediLens could not process this image. "
                "Please try a clearer medicine photograph."
            ),
        )

    # --------------------------------------------------------
    # Remove temporary uploaded image
    # --------------------------------------------------------

    try:
        image_path.unlink(missing_ok=True)
    except Exception:
        pass

    # --------------------------------------------------------
    # Prepare audio URLs
    # --------------------------------------------------------

    medicines = result.get("medicines", [])

    for medicine in medicines:
        original_audio_path = medicine.get("audio_path")

        audio_url = prepare_audio_file(original_audio_path)

        medicine["audio_url"] = audio_url

        # Do not expose the local Windows file path to React.
        medicine.pop("audio_path", None)

    # --------------------------------------------------------
    # Add API metadata
    # --------------------------------------------------------

    result["language"] = language

    return result


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )