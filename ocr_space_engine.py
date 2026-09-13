"""
ocr_space_engine.py

Lightweight cloud OCR pipeline for MediLens.AI deployment.
Uses OCR.space for OCR so Render Free does not need EasyOCR/PyTorch.
Keeps the existing DrugMatcher + translations + gTTS workflow.
"""

import os
import re
from pathlib import Path
from io import BytesIO
from typing import Any, Dict, List, Tuple

import requests
from PIL import Image
from drug_lookup_medeye import DrugMatcher
from speak_test import generate_audio

OCR_URL = "https://api.ocr.space/parse/image"
OCR_API_KEY = os.getenv("OCR_SPACE_API_KEY", "")
OCR_ENGINE = os.getenv("OCR_SPACE_ENGINE", "2")


def looks_like_noise(text: str) -> bool:
    if not text:
        return True
    text = str(text).strip()
    if len(text) < 2:
        return True
    compact = re.sub(r"[^a-zA-Z0-9]", "", text)
    if not compact or compact.isdigit():
        return True
    if not re.search(r"[a-zA-Z]", compact):
        return True
    return False


class MediLensCloudOCR:
    def __init__(self):
        if not OCR_API_KEY:
            raise RuntimeError("OCR_SPACE_API_KEY is not configured on the server.")

        # Use the final database when present; fall back to the older filename.
        final_db = Path("drugs_tagged_final.csv")
        old_db = Path("drugs_expanded_fixed.csv")
        if final_db.exists():
            self.matcher = DrugMatcher(str(final_db))
        else:
            self.matcher = DrugMatcher(str(old_db))

    def run_ocr(self, image_path: str) -> Tuple[List[Dict[str, Any]], str]:
        """Send one image to OCR.space and return line detections + full text."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # OCR.space free API accepts files up to 1 MB. Compress oversized
        # uploads in memory so normal phone photos do not fail immediately.
        raw_bytes = path.read_bytes()
        upload_name = path.name
        upload_bytes = raw_bytes
        mime_type = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"

        if len(raw_bytes) > 900_000:
            with Image.open(BytesIO(raw_bytes)) as source:
                image = source.convert("RGB")
                image.thumbnail((1800, 1800))
                buffer = BytesIO()
                quality = 85
                image.save(buffer, format="JPEG", quality=quality, optimize=True)
                while buffer.tell() > 900_000 and quality >= 50:
                    buffer = BytesIO()
                    quality -= 5
                    image.save(buffer, format="JPEG", quality=quality, optimize=True)
                upload_bytes = buffer.getvalue()
                upload_name = f"{path.stem}.jpg"
                mime_type = "image/jpeg"

        response = requests.post(
            OCR_URL,
            headers={"apikey": OCR_API_KEY},
            files={"file": (upload_name, upload_bytes, mime_type)},
            data={
                "language": "eng",
                "OCREngine": OCR_ENGINE,
                "isOverlayRequired": "false",
                "scale": "true",
                "detectOrientation": "true",
            },
            timeout=60,
        )

        response.raise_for_status()
        payload = response.json()

        if payload.get("IsErroredOnProcessing"):
            errors = payload.get("ErrorMessage") or payload.get("ErrorDetails") or "OCR.space processing failed."
            if isinstance(errors, list):
                errors = " ".join(str(x) for x in errors)
            raise RuntimeError(str(errors))

        parsed = payload.get("ParsedResults") or []
        detections: List[Dict[str, Any]] = []
        all_text: List[str] = []

        for result in parsed:
            text = str(result.get("ParsedText") or "").strip()
            if not text:
                continue
            all_text.append(text)

            # OCR.space does not expose the same numeric confidence field as EasyOCR.
            # Keep a neutral internal value; the visible medicine confidence is driven
            # by the database match score instead of pretending this is EasyOCR confidence.
            for line in text.splitlines():
                line = " ".join(line.split()).strip()
                if looks_like_noise(line):
                    continue
                detections.append({"text": line, "confidence": None})

        return detections, "\n".join(all_text).strip()

    def match_medicines(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        accepted: List[Dict[str, Any]] = []

        for item in detections:
            text = item["text"]
            try:
                info, score, method = self.matcher.match_term(
                    text,
                    min_score=70.0,
                    ambiguity_margin=5.0,
                )
            except Exception as exc:
                print(f"Matcher error for {text!r}: {exc}")
                continue

            if info is None:
                continue

            medicine = dict(info)
            medicine["ocr_text"] = text
            medicine["ocr_confidence"] = None
            medicine["match_score"] = round(float(score), 2) if score is not None else None
            medicine["match_method"] = method
            accepted.append(medicine)

        # Keep the strongest result for each canonical medicine.
        best: Dict[str, Dict[str, Any]] = {}
        for medicine in accepted:
            name = str(medicine.get("name", "")).strip()
            key = name.lower()
            score = medicine.get("match_score") or 0
            if key not in best or score > (best[key].get("match_score") or 0):
                best[key] = medicine

        return sorted(
            best.values(),
            key=lambda x: x.get("match_score") or 0,
            reverse=True,
        )

    def process_image(self, image_path: str, voice_language: str = "en") -> Dict[str, Any]:
        detections, full_text = self.run_ocr(image_path)
        medicines = self.match_medicines(detections)

        for medicine in medicines:
            speech_info = {
                "name": medicine.get("name", ""),
                "typical_dosage": medicine.get("typical_dosage", ""),
                "category": medicine.get("category", "general"),
                "key_warning": medicine.get("key_warning", ""),
                "common_side_effects": medicine.get("common_side_effects", ""),
                "warnings": medicine.get("warnings", ""),
                "commonly_used_for": medicine.get("commonly_used_for", ""),
            }

            try:
                audio_path, spoken_text = generate_audio(speech_info, voice_language)
                medicine["audio_path"] = audio_path
                medicine["spoken_text"] = spoken_text
            except Exception as exc:
                print(f"Voice generation failed for {medicine.get('name')}: {exc}")
                medicine["audio_path"] = None
                medicine["spoken_text"] = None

        return {
            "success": True,
            "image": image_path,
            "ocr_text": detections,
            "ocr_full_text": full_text,
            "medicines": medicines,
            "error": None,
        }
