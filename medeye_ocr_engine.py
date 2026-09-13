"""
medeye_ocr_engine.py

MediLens.AI OCR Engine

Pipeline:
Image
  ↓
Image preprocessing
  ↓
EasyOCR on multiple variants
  ↓
OCR noise filtering
  ↓
Drug database matching
  ↓
Medicine-level consensus and deduplication
  ↓
Final medicine information
  ↓
Automatic multilingual voice

Important:
- The engine is conservative about medicine identification.
- A weak or ambiguous OCR result is not treated as a confirmed medicine.
- Multiple OCR readings of the same medicine are combined.
- Automatic local voice playback remains enabled by default.
- For a web backend, process_image(..., play_voice=False) can be used so
  the frontend can play the generated MP3 instead.
"""

import sys
import re
from typing import Any, Dict, List

import easyocr

from image_processing import ImagePreprocessor
from drug_lookup_medeye import DrugMatcher
from speak_test import generate_audio, play_audio


# =========================================================
# CONFIGURATION
# =========================================================

OCR_CONFIDENCE_THRESHOLD = 0.45
MATCH_CONFIDENCE_THRESHOLD = 70.0

# A medicine should normally have either:
# 1. an exact database/alias match, or
# 2. a strong fuzzy match.
#
# This margin is used only as an additional safety check when
# several OCR readings compete for the same medicine.
CONSENSUS_MIN_READINGS = 2


# =========================================================
# OCR NOISE FILTER
# =========================================================

def looks_like_noise(text: str) -> bool:
    """
    Reject obvious OCR noise such as:
    - empty text
    - one-character text
    - numbers only
    - symbols only
    - text containing no alphabetic characters
    """

    if not text:
        return True

    text = str(text).strip()

    if len(text) < 2:
        return True

    compact = re.sub(
        r"[^a-zA-Z0-9]",
        "",
        text
    )

    if not compact:
        return True

    # Ignore text containing only numbers.
    if compact.isdigit():
        return True

    # Ignore text containing no letters.
    if not re.search(
        r"[a-zA-Z]",
        compact
    ):
        return True

    return False


# =========================================================
# MEDILENS OCR CLASS
# =========================================================

class MediLensOCR:

    def __init__(self):

        print("Loading EasyOCR model...")

        self.reader = easyocr.Reader(
            ["en"],
            gpu=False
        )

        print("EasyOCR ready.")

        self.preprocessor = ImagePreprocessor()

        self.matcher = DrugMatcher()


    # =====================================================
    # RUN OCR ON ONE IMAGE
    # =====================================================

    def run_ocr(
        self,
        image
    ) -> List[Dict[str, Any]]:

        detections = []

        try:

            results = self.reader.readtext(
                image,
                detail=1,
                paragraph=False
            )

        except Exception as error:

            print(
                f"OCR error: {error}"
            )

            return detections


        for result in results:

            if len(result) < 3:
                continue

            _, text, confidence = result

            text = str(text).strip()

            try:

                confidence = float(
                    confidence
                )

            except (
                TypeError,
                ValueError
            ):

                continue


            if not text:
                continue


            if confidence < OCR_CONFIDENCE_THRESHOLD:
                continue


            if looks_like_noise(text):
                continue


            detections.append(
                {
                    "text": text,
                    "confidence": confidence
                }
            )


        return detections


    # =====================================================
    # DEDUPLICATE OCR TEXT
    # =====================================================

    def deduplicate_text(
        self,
        detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        unique = {}

        for item in detections:

            text = str(
                item.get("text", "")
            ).strip()

            if not text:
                continue

            # Normalize spacing/case for exact OCR deduplication.
            key = " ".join(
                text.lower().split()
            )

            if key not in unique:

                unique[key] = dict(item)

            else:

                # Keep the strongest OCR confidence.
                if (
                    float(item.get("confidence", 0))
                    >
                    float(
                        unique[key].get(
                            "confidence",
                            0
                        )
                    )
                ):

                    unique[key] = dict(item)


        return list(
            unique.values()
        )


    # =====================================================
    # MATCH OCR TEXT TO MEDICINES
    # =====================================================

    def match_medicines(
        self,
        detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        all_matches = []

        for item in detections:

            ocr_text = str(
                item.get(
                    "text",
                    ""
                )
            ).strip()

            ocr_confidence = float(
                item.get(
                    "confidence",
                    0
                )
            )

            if not ocr_text:
                continue


            try:

                drug_info, match_score, status = (
                    self.matcher.match_term(
                        ocr_text,
                        min_score=(
                            MATCH_CONFIDENCE_THRESHOLD
                        )
                    )
                )

            except Exception as error:

                print(
                    f"Matching error for "
                    f"'{ocr_text}': {error}"
                )

                continue


            # -------------------------------------------------
            # IMPORTANT SAFETY RULE
            #
            # If the matcher rejects the text, do not guess
            # the medicine from a weak fuzzy result.
            # -------------------------------------------------

            if drug_info is None:
                continue


            try:

                match_score = float(
                    match_score
                )

            except (
                TypeError,
                ValueError
            ):

                continue


            result = dict(
                drug_info
            )

            result["ocr_text"] = ocr_text

            result["ocr_confidence"] = (
                ocr_confidence
            )

            result["match_score"] = (
                match_score
            )

            result["match_status"] = (
                status
            )

            all_matches.append(
                result
            )


        return all_matches


    # =====================================================
    # MEDICINE RESULT STRENGTH
    # =====================================================

    @staticmethod
    def _match_priority(
        status: str
    ) -> int:
        """
        Rank matching methods.

        Exact canonical / alias matches are more trustworthy
        than fuzzy matches even when a fuzzy result happens
        to have a high numerical score.
        """

        status = str(
            status or ""
        ).upper()

        if status == "EXACT_CANONICAL":
            return 4

        if status == "EXACT_ALIAS":
            return 3

        if "FUZZY" in status:
            return 2

        return 1


    @classmethod
    def _result_strength(
        cls,
        result: Dict[str, Any]
    ) -> float:
        """
        Calculate a combined strength score.

        This is NOT presented as medical certainty.

        It simply helps choose the strongest OCR/database
        evidence when several OCR variants refer to the
        same medicine.
        """

        match_score = float(
            result.get(
                "match_score",
                0
            )
        )

        ocr_confidence = float(
            result.get(
                "ocr_confidence",
                0
            )
        )

        priority = cls._match_priority(
            result.get(
                "match_status",
                ""
            )
        )

        # Convert OCR confidence to percentage.
        ocr_percentage = (
            ocr_confidence * 100
        )

        # Match score receives more weight because the
        # database relationship is important.
        combined = (
            match_score * 0.65
            +
            ocr_percentage * 0.35
        )

        # Small bonus for exact database matches.
        if priority == 4:
            combined += 5.0

        elif priority == 3:
            combined += 3.0

        return combined


    # =====================================================
    # MEDICINE-LEVEL CONSENSUS
    # =====================================================

    def deduplicate_medicines(
        self,
        matches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Combine different OCR readings that map to the same
        medicine.

        Example:

            Okacet  -> Cetirizine
            Okacat  -> Cetirizine
            Oacet   -> Cetirizine

        Final result:

            Cetirizine
            Best OCR reading: Okacet
            Other OCR readings: Okacat, Oacet

        The strongest database/OCR evidence is retained as
        the primary result.
        """

        grouped = {}


        # -----------------------------------------------------
        # GROUP BY CANONICAL MEDICINE NAME
        # -----------------------------------------------------

        for match in matches:

            medicine_name = str(
                match.get(
                    "name",
                    ""
                )
            ).strip()

            if not medicine_name:
                continue

            key = medicine_name.lower()


            if key not in grouped:

                result = dict(match)

                result[
                    "alternative_ocr_readings"
                ] = []

                result[
                    "ocr_reading_count"
                ] = 1

                grouped[key] = result

                continue


            existing = grouped[key]


            # -------------------------------------------------
            # COUNT OCR READINGS
            # -------------------------------------------------

            existing[
                "ocr_reading_count"
            ] = int(
                existing.get(
                    "ocr_reading_count",
                    1
                )
            ) + 1


            # -------------------------------------------------
            # SAVE DIFFERENT OCR READINGS
            # -------------------------------------------------

            existing_text = str(
                existing.get(
                    "ocr_text",
                    ""
                )
            ).strip()

            current_text = str(
                match.get(
                    "ocr_text",
                    ""
                )
            ).strip()


            if (
                current_text
                and
                current_text.lower()
                != existing_text.lower()
            ):

                alternatives = existing[
                    "alternative_ocr_readings"
                ]

                already_present = any(
                    str(value).lower()
                    ==
                    current_text.lower()
                    for value in alternatives
                )

                if not already_present:

                    alternatives.append(
                        current_text
                    )


            # -------------------------------------------------
            # KEEP STRONGEST PRIMARY RESULT
            # -------------------------------------------------

            existing_strength = (
                self._result_strength(
                    existing
                )
            )

            current_strength = (
                self._result_strength(
                    match
                )
            )


            if current_strength > existing_strength:

                alternative_readings = (
                    existing.get(
                        "alternative_ocr_readings",
                        []
                    )
                )

                previous_primary = (
                    existing.get(
                        "ocr_text",
                        ""
                    )
                )

                new_result = dict(
                    match
                )

                new_result[
                    "alternative_ocr_readings"
                ] = list(
                    alternative_readings
                )

                if (
                    previous_primary
                    and
                    previous_primary.lower()
                    !=
                    str(
                        new_result.get(
                            "ocr_text",
                            ""
                        )
                    ).lower()
                ):

                    already_present = any(
                        str(value).lower()
                        ==
                        previous_primary.lower()
                        for value
                        in
                        new_result[
                            "alternative_ocr_readings"
                        ]
                    )

                    if not already_present:

                        new_result[
                            "alternative_ocr_readings"
                        ].append(
                            previous_primary
                        )


                new_result[
                    "ocr_reading_count"
                ] = existing.get(
                    "ocr_reading_count",
                    1
                )

                grouped[key] = (
                    new_result
                )


        # -----------------------------------------------------
        # SORT BY EVIDENCE
        # -----------------------------------------------------

        results = list(
            grouped.values()
        )

        results.sort(
            key=self._result_strength,
            reverse=True
        )


        # -----------------------------------------------------
        # REMOVE DUPLICATE ALTERNATIVES
        # -----------------------------------------------------

        for result in results:

            primary = str(
                result.get(
                    "ocr_text",
                    ""
                )
            ).strip().lower()

            cleaned = []

            for value in result.get(
                "alternative_ocr_readings",
                []
            ):

                value = str(
                    value
                ).strip()

                if not value:
                    continue

                if value.lower() == primary:
                    continue

                if value.lower() not in [
                    str(x).lower()
                    for x in cleaned
                ]:

                    cleaned.append(
                        value
                    )

            result[
                "alternative_ocr_readings"
            ] = cleaned


        return results


    # =====================================================
    # AUTOMATIC VOICE
    # =====================================================

    def speak_medicines(
        self,
        medicines: List[Dict[str, Any]],
        language: str = "en",
        play_voice: bool = True
    ):
        """
        Generate voice for every confidently identified
        medicine.

        By default:
            play_voice=True

        This preserves the current local behaviour where the
        generated medicine information is automatically spoken.

        For a web backend:
            play_voice=False

        The MP3 is still generated and returned in the result,
        allowing the frontend/browser to play it.
        """

        if not medicines:

            print()

            print(
                "No medicine identified, "
                "so there is no voice output."
            )

            return


        print()

        print(
            "=" * 60
        )

        print(
            "VOICE OUTPUT"
        )

        print(
            "=" * 60
        )


        for medicine in medicines:

            medicine_name = str(
                medicine.get(
                    "name",
                    "Unknown medicine"
                )
            ).strip()


            # -------------------------------------------------
            # Collect medicine information safely.
            #
            # IMPORTANT:
            # Do NOT insert "Not specified in the database"
            # into speech. That phrase was making the voice
            # sound unnatural.
            # -------------------------------------------------

            speech_info = {

                "name":
                    medicine_name,

                "typical_dosage":
                    medicine.get(
                        "typical_dosage",
                        ""
                    ),

                "category":
                    medicine.get(
                        "category",
                        "general"
                    ),

                "key_warning":
                    medicine.get(
                        "key_warning",
                        ""
                    ),

                "common_side_effects":
                    medicine.get(
                        "common_side_effects",
                        ""
                    ),

                "warnings":
                    medicine.get(
                        "warnings",
                        ""
                    ),

                "commonly_used_for":
                    medicine.get(
                        "commonly_used_for",
                        ""
                    ),
            }


            try:

                print()

                print(
                    f"Preparing voice for "
                    f"{medicine_name}..."
                )


                # -------------------------------------------------
                # GENERATE AUDIO
                # -------------------------------------------------

                audio_path, sentence = (
                    generate_audio(
                        speech_info,
                        language
                    )
                )


                medicine[
                    "audio_path"
                ] = audio_path

                medicine[
                    "spoken_text"
                ] = sentence


                print()

                print(
                    "Speech:"
                )

                print(
                    sentence
                )


                # -------------------------------------------------
                # AUTOMATIC LOCAL PLAYBACK
                # -------------------------------------------------

                if play_voice:

                    print()

                    print(
                        "Playing medicine information..."
                    )

                    played = play_audio(
                        audio_path
                    )

                    medicine[
                        "audio_played"
                    ] = played


                    if played:

                        print(
                            "Voice playback completed."
                        )

                    else:

                        print(
                            "Audio was generated, "
                            "but automatic playback failed."
                        )

                else:

                    # Web deployment mode.
                    medicine[
                        "audio_played"
                    ] = False

                    print()

                    print(
                        "Audio generated for frontend playback."
                    )


            except Exception as error:

                medicine[
                    "audio_path"
                ] = None

                medicine[
                    "spoken_text"
                ] = None

                medicine[
                    "audio_played"
                ] = False


                print()

                print(
                    "Voice generation/playback "
                    f"failed for {medicine_name}:"
                )

                print(
                    f"   {error}"
                )


    # =====================================================
    # COMPLETE PIPELINE
    # =====================================================

    def process_image(
        self,
        image_path: str,
        voice_language: str = "en",
        play_voice: bool = True
    ) -> Dict[str, Any]:

        print()

        print(
            "=" * 60
        )

        print(
            "MEDILENS.AI OCR ENGINE"
        )

        print(
            "=" * 60
        )

        print(
            f"Image: {image_path}"
        )


        # =================================================
        # STEP 1 — PREPROCESSING
        # =================================================

        print()

        print(
            "Step 1: Image preprocessing..."
        )


        try:

            variants = (
                self.preprocessor.preprocess(
                    image_path
                )
            )

        except Exception as error:

            print(
                f"Preprocessing failed: "
                f"{error}"
            )

            return {
                "success": False,
                "image": image_path,
                "ocr_text": [],
                "medicines": [],
                "error": str(error)
            }


        # Support both:
        #   dict:  {"original": image, ...}
        #   list:  [("original", image), ...]
        #
        # This keeps the engine compatible with the
        # preprocessing implementations used in the project.

        if isinstance(
            variants,
            dict
        ):

            variant_items = (
                list(
                    variants.items()
                )
            )

        elif isinstance(
            variants,
            list
        ):

            variant_items = (
                variants
            )

        else:

            print(
                "Preprocessor returned "
                "an unsupported format."
            )

            return {
                "success": False,
                "image": image_path,
                "ocr_text": [],
                "medicines": [],
                "error":
                    "Unsupported preprocessing output."
            }


        print(
            f"Created {len(variant_items)} "
            f"image variants."
        )


        # =================================================
        # STEP 2 — OCR
        # =================================================

        print()

        print(
            "Step 2: Running EasyOCR..."
        )


        all_detections = []


        for variant_name, image in (
            variant_items
        ):

            print(
                f"  -> Processing: "
                f"{variant_name}"
            )


            detections = self.run_ocr(
                image
            )


            for detection in detections:

                detection[
                    "variant"
                ] = variant_name

                all_detections.append(
                    detection
                )


        # =================================================
        # REMOVE DUPLICATE OCR TEXT
        # =================================================

        unique_detections = (
            self.deduplicate_text(
                all_detections
            )
        )


        # Sort highest OCR confidence first.
        unique_detections.sort(
            key=lambda item:
                float(
                    item.get(
                        "confidence",
                        0
                    )
                ),
            reverse=True
        )


        print()

        print(
            f"Reliable OCR text items: "
            f"{len(unique_detections)}"
        )


        # =================================================
        # DISPLAY OCR TEXT
        # =================================================

        print()

        print(
            "Detected text:"
        )


        if not unique_detections:

            print(
                "  No reliable text detected."
            )

        else:

            for item in (
                unique_detections
            ):

                print(
                    f"  {item['text']} "
                    f"(OCR confidence: "
                    f"{item['confidence']:.2f})"
                )


        # =================================================
        # STEP 3 — MEDICINE MATCHING
        # =================================================

        print()

        print(
            "Step 3: Matching detected text "
            "with medicine database..."
        )


        all_matches = (
            self.match_medicines(
                unique_detections
            )
        )


        print(
            f"Accepted medicine matches: "
            f"{len(all_matches)}"
        )


        # =================================================
        # STEP 4 — MEDICINE CONSENSUS
        # =================================================

        print()

        print(
            "Step 4: Combining OCR readings "
            "for the same medicine..."
        )


        medicines = (
            self.deduplicate_medicines(
                all_matches
            )
        )


        # =================================================
        # FINAL MEDICINE RESULTS
        # =================================================

        print()

        print(
            "=" * 60
        )

        print(
            "FINAL MEDICINE RESULTS"
        )

        print(
            "=" * 60
        )


        if not medicines:

            print()

            print(
                "No confident medicine "
                "match found."
            )

        else:

            for medicine in medicines:

                print()

                print(
                    f"Medicine: "
                    f"{medicine.get('name', 'Unknown')}"
                )


                print(
                    f"Best OCR reading: "
                    f"{medicine.get('ocr_text', '')}"
                )


                print(
                    f"OCR confidence: "
                    f"{medicine.get('ocr_confidence', 0):.2f}"
                )


                print(
                    f"Match score: "
                    f"{medicine.get('match_score', 0):.1f}%"
                )


                print(
                    f"Match type: "
                    f"{medicine.get('match_status', '')}"
                )


                print(
                    f"OCR readings supporting result: "
                    f"{medicine.get('ocr_reading_count', 1)}"
                )


                alternatives = medicine.get(
                    "alternative_ocr_readings",
                    []
                )


                if alternatives:

                    print(
                        "Other OCR readings: "
                        +
                        ", ".join(
                            alternatives
                        )
                    )


                if medicine.get(
                    "dosage_forms"
                ):

                    print(
                        f"Dosage form: "
                        f"{medicine['dosage_forms']}"
                    )


                if medicine.get(
                    "typical_dosage"
                ):

                    print(
                        f"Typical dosage: "
                        f"{medicine['typical_dosage']}"
                    )


                if medicine.get(
                    "commonly_used_for"
                ):

                    print(
                        f"Commonly used for: "
                        f"{medicine['commonly_used_for']}"
                    )


                if medicine.get(
                    "common_side_effects"
                ):

                    print(
                        f"Common side effects: "
                        f"{medicine['common_side_effects']}"
                    )


                if medicine.get(
                    "warnings"
                ):

                    print(
                        f"Warnings: "
                        f"{medicine['warnings']}"
                    )


                if medicine.get(
                    "category"
                ):

                    print(
                        f"Category: "
                        f"{medicine['category']}"
                    )


        # =================================================
        # STEP 5 — AUTOMATIC VOICE
        # =================================================

        self.speak_medicines(
            medicines,
            language=voice_language,
            play_voice=play_voice
        )


        # =================================================
        # COMPLETE
        # =================================================

        print()

        print(
            "=" * 60
        )

        print(
            "MEDILENS.AI PROCESSING COMPLETE"
        )

        print(
            "=" * 60
        )


        return {
            "success": True,
            "image": image_path,
            "ocr_text": unique_detections,
            "medicines": medicines,
            "error": None
        }


# =========================================================
# COMMAND LINE ENTRY
# =========================================================

def main():

    if len(sys.argv) < 2:

        print()

        print(
            "Usage:"
        )

        print(
            'python medeye_ocr_engine.py "path_to_image"'
        )

        print()

        print(
            "Examples:"
        )

        print(
            'python medeye_ocr_engine.py "med3.jpeg"'
        )

        print(
            'python medeye_ocr_engine.py "med3.jpeg" --lang te'
        )

        print(
            'python medeye_ocr_engine.py "med3.jpeg" --lang hi'
        )

        print(
            'python medeye_ocr_engine.py "med3.jpeg" --no-play'
        )

        return


    image_path = None

    language = "en"

    play_voice = True


    # -----------------------------------------------------
    # READ COMMAND LINE ARGUMENTS
    # -----------------------------------------------------

    arguments = sys.argv[1:]

    i = 0


    while i < len(arguments):

        argument = arguments[i]


        # -------------------------------------------------
        # --lang te
        # -------------------------------------------------

        if argument == "--lang":

            if i + 1 < len(arguments):

                language = (
                    arguments[i + 1]
                )

                i += 2

                continue


        # -------------------------------------------------
        # --lang=te
        # -------------------------------------------------

        elif argument.startswith(
            "--lang="
        ):

            language = argument.split(
                "=",
                1
            )[1]

            i += 1

            continue


        # -------------------------------------------------
        # --no-play
        #
        # Useful when running the backend/server because
        # the browser should play the MP3, not the server.
        # -------------------------------------------------

        elif argument == "--no-play":

            play_voice = False

            i += 1

            continue


        # -------------------------------------------------
        # IMAGE PATH
        # -------------------------------------------------

        if (
            not argument.startswith("--")
            and image_path is None
        ):

            image_path = argument


        i += 1


    # -----------------------------------------------------
    # VALIDATE LANGUAGE
    # -----------------------------------------------------

    if language not in (
        "en",
        "te",
        "hi"
    ):

        print(
            f"Invalid language: {language}"
        )

        print(
            "Use: en, te, or hi"
        )

        return


    # -----------------------------------------------------
    # VALIDATE IMAGE
    # -----------------------------------------------------

    if not image_path:

        print(
            "Please provide an image path."
        )

        return


    # -----------------------------------------------------
    # START ENGINE
    # -----------------------------------------------------

    engine = MediLensOCR()


    engine.process_image(
        image_path,
        voice_language=language,
        play_voice=play_voice
    )


# =========================================================
# START PROGRAM
# =========================================================

if __name__ == "__main__":

    main()