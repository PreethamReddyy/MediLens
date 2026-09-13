"""
speak_test.py

MediLens.AI automatic multilingual speech.

Generates cached MP3 speech using gTTS
and automatically plays it on Windows.

The generated speech includes:
- Medicine name
- Common use
- Typical dosage
- Common side effects
- Important warning
"""

import hashlib
import os
import re


# =========================================================
# AUDIO DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

AUDIO_DIR = os.path.join(
    BASE_DIR,
    "audio_cache"
)

os.makedirs(
    AUDIO_DIR,
    exist_ok=True
)


# =========================================================
# SUPPORTED LANGUAGES
# =========================================================

LANGUAGES = {
    "en": "English",
    "te": "Telugu",
    "hi": "Hindi",
}


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_for_speech(text):
    """
    Clean text before sending it to gTTS.
    """

    if text is None:
        return ""

    text = str(text).strip()

    if not text:
        return ""

    # Remove excessive whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # Make common medicine units easier to pronounce.
    text = re.sub(
        r"(\d+)\s*mg\b",
        r"\1 milligrams",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"(\d+)\s*ml\b",
        r"\1 milliliters",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"(\d+)\s*g\b",
        r"\1 grams",
        text,
        flags=re.IGNORECASE
    )

    return text


# =========================================================
# SIDE EFFECT CLEANING
# =========================================================

def clean_side_effects(value):
    """
    Convert database side effects into a clean list.

    Supports:
        "drowsiness, dry mouth, headache"
        "drowsiness; dry mouth; headache"
        "drowsiness and headache"
    """

    if value is None:
        return []

    text = str(value).strip()

    if not text:
        return []

    # Remove database-style fallback text if it somehow
    # exists in an old CSV.
    invalid_values = {
        "",
        "nan",
        "none",
        "not specified",
        "not specified in the database",
        "not mentioned in the database",
        "n/a",
        "na",
    }

    if text.lower() in invalid_values:
        return []

    # Normalize separators.
    text = re.sub(
        r"\s*;\s*",
        ",",
        text
    )

    # Split commas.
    parts = [
        part.strip()
        for part in text.split(",")
    ]

    cleaned = []

    for part in parts:

        part = part.strip(
            " .;"
        )

        if not part:
            continue

        if part.lower() in invalid_values:
            continue

        if part.lower() not in [
            item.lower()
            for item in cleaned
        ]:

            cleaned.append(
                part
            )

    return cleaned


# =========================================================
# BUILD NATURAL ENGLISH SPEECH
# =========================================================

def build_english_speech(info):
    """
    Build a natural English medicine explanation.

    Example:

    "Cetirizine. This medicine is commonly used for
    allergic rhinitis, hives, and itching. The usual dose
    is 10 milligrams once daily. Common side effects include
    drowsiness, dry mouth, headache, and fatigue. It may
    cause drowsiness, so avoid driving until you know how
    it affects you. Avoid alcohol."
    """

    name = str(
        info.get(
            "name",
            "Unknown medicine"
        )
    ).strip()

    purpose = str(
        info.get(
            "commonly_used_for",
            ""
        ) or ""
    ).strip()

    dosage = str(
        info.get(
            "typical_dosage",
            ""
        ) or ""
    ).strip()

    side_effects = clean_side_effects(
        info.get(
            "common_side_effects",
            ""
        )
    )

    warning = str(
        info.get(
            "warnings",
            ""
        ) or ""
    ).strip()


    sentences = []


    # -----------------------------------------------------
    # MEDICINE NAME
    # -----------------------------------------------------

    if name:

        sentences.append(
            f"{name}."
        )


    # -----------------------------------------------------
    # COMMON USE
    # -----------------------------------------------------

    if purpose:

        sentences.append(
            "This medicine is commonly used for "
            f"{purpose}."
        )


    # -----------------------------------------------------
    # DOSAGE
    # -----------------------------------------------------

    if dosage:

        dosage_text = clean_for_speech(
            dosage
        )

        sentences.append(
            "The usual dose is "
            f"{dosage_text}."
        )

    else:

        sentences.append(
            "For dosage, follow your doctor's instructions."
        )


    # -----------------------------------------------------
    # SIDE EFFECTS
    # -----------------------------------------------------

    if side_effects:

        if len(side_effects) == 1:

            effects_text = (
                side_effects[0]
            )

        elif len(side_effects) == 2:

            effects_text = (
                f"{side_effects[0]} and "
                f"{side_effects[1]}"
            )

        else:

            effects_text = (
                ", ".join(
                    side_effects[:-1]
                )
                +
                ", and "
                +
                side_effects[-1]
            )


        sentences.append(
            "Common side effects include "
            f"{effects_text}."
        )


    # -----------------------------------------------------
    # WARNING
    # -----------------------------------------------------

    if warning:

        warning = clean_for_speech(
            warning
        )

        sentences.append(
            warning
        )


    return " ".join(
        sentences
    )


# =========================================================
# GENERATE AUDIO
# =========================================================

def generate_audio(
    info: dict,
    lang: str = "en"
):
    """
    Generate medicine-information speech.

    Returns:
        audio_path, sentence
    """

    from gtts import gTTS

    if lang not in LANGUAGES:

        lang = "en"


    # -----------------------------------------------------
    # BUILD SPEECH
    # -----------------------------------------------------

    if lang == "en":

        sentence = build_english_speech(
            info
        )

    else:

        # Telugu and Hindi continue to use the project's
        # curated translation system.
        from translations import build_sentence

        sentence = build_sentence(
            info,
            lang
        )


    sentence = clean_for_speech(
        sentence
    )


    # -----------------------------------------------------
    # CACHE NAME
    # -----------------------------------------------------

    key = hashlib.sha256(
        f"{lang}|{sentence}".encode(
            "utf-8"
        )
    ).hexdigest()[:16]


    safe_name = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        str(
            info.get(
                "name",
                "medicine"
            )
        )
    ).strip("_")


    filename = (
        f"{safe_name}_{lang}_{key}.mp3"
    )


    audio_path = os.path.join(
        AUDIO_DIR,
        filename
    )


    # -----------------------------------------------------
    # GENERATE AUDIO
    # -----------------------------------------------------

    if (
        not os.path.exists(
            audio_path
        )
        or
        os.path.getsize(
            audio_path
        ) < 1024
    ):

        print(
            "\nGenerating clear voice..."
        )

        tts = gTTS(
            text=sentence,
            lang=lang,
            slow=False
        )

        tts.save(
            audio_path
        )

        print(
            "Voice generated."
        )

    else:

        print(
            "\nUsing cached voice..."
        )


    return (
        audio_path,
        sentence
    )


# =========================================================
# PLAY AUDIO
# =========================================================

def play_audio(
    audio_path: str
):
    """
    Automatically play generated speech.

    Uses multiple playback methods so that
    failure of one method does not immediately
    stop audio playback.
    """

    if not audio_path:

        print(
            "No audio file."
        )

        return False


    if not os.path.isfile(
        audio_path
    ):

        print(
            f"Audio file not found:\n"
            f"{audio_path}"
        )

        return False


    print(
        "\nSpeaking medicine information..."
    )


    # =====================================================
    # METHOD 1 — PLAYSOUND
    # =====================================================

    try:

        from playsound import (
            playsound
        )

        playsound(
            audio_path
        )

        print(
            "Voice completed."
        )

        return True

    except Exception as error:

        print(
            "playsound failed."
        )

        print(
            f"   {error}"
        )


    # =====================================================
    # METHOD 2 — PYGAME
    # =====================================================

    try:

        import pygame

        pygame.mixer.init()

        pygame.mixer.music.load(
            audio_path
        )

        pygame.mixer.music.set_volume(
            1.0
        )

        pygame.mixer.music.play()

        clock = pygame.time.Clock()

        while pygame.mixer.music.get_busy():

            clock.tick(10)


        pygame.mixer.music.stop()

        pygame.mixer.quit()

        print(
            "Voice completed."
        )

        return True

    except Exception as error:

        print(
            "pygame playback failed."
        )

        print(
            f"   {error}"
        )


    # =====================================================
    # METHOD 3 — WINDOWS
    # =====================================================

    if os.name == "nt":

        try:

            os.startfile(
                audio_path
            )

            print(
                "Audio opened in Windows "
                "media player."
            )

            return True

        except Exception as error:

            print(
                "Windows playback failed."
            )

            print(
                f"   {error}"
            )


    # =====================================================
    # FAILURE
    # =====================================================

    print(
        "\nAutomatic audio playback failed."
    )

    print(
        f"Audio file:\n{audio_path}"
    )

    return False


# =========================================================
# DIRECT TEST
# =========================================================

if __name__ == "__main__":

    test_info = {

        "name":
            "Cetirizine",

        "typical_dosage":
            "10mg once daily",

        "category":
            "allergy",

        "key_warning":
            "drowsiness",

        "commonly_used_for":
            "Allergic rhinitis, hives, and itching",

        "common_side_effects":
            "drowsiness, dry mouth, headache, fatigue",

        "warnings":
            "May cause drowsiness. Avoid driving until you know how it affects you. Avoid alcohol.",
    }


    print(
        "\n========================================"
    )

    print(
        "       MEDILENS.AI VOICE TEST"
    )

    print(
        "========================================"
    )


    audio_path, sentence = (
        generate_audio(
            test_info,
            "te"
        )
    )


    print(
        "\nSpeech:"
    )

    print(
        sentence
    )


    play_audio(
        audio_path
    )