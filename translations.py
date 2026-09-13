
"""
translations.py

MediLens.AI speech-language module.

Creates short, clear and natural medicine-information sentences
for English, Telugu and Hindi.

Spoken information:
1. Medicine name
2. What the medicine is commonly used for
3. Typical dosage from the database
4. Up to four common side effects from the database
5. Important warning

Important:
The system does not invent medical information. It speaks the
information available in the medicine database.
"""


# =========================================================
# CATEGORY / PURPOSE PHRASES
# =========================================================

CATEGORY_PHRASES = {

    "high_blood_pressure": {
        "en": "high blood pressure",
        "te": "అధిక రక్తపోటు",
        "hi": "उच्च रक्तचाप",
    },

    "diabetes": {
        "en": "diabetes",
        "te": "మధుమేహం",
        "hi": "मधुमेह",
    },

    "allergy": {
        "en": "allergy symptoms",
        "te": "అలర్జీ లక్షణాలు",
        "hi": "एलर्जी के लक्षण",
    },

    "antibiotic": {
        "en": "bacterial infections",
        "te": "బ్యాక్టీరియా ఇన్ఫెక్షన్లు",
        "hi": "बैक्टीरियल संक्रमण",
    },

    "antifungal": {
        "en": "fungal infections",
        "te": "ఫంగల్ ఇన్ఫెక్షన్లు",
        "hi": "फंगल संक्रमण",
    },

    "acidity": {
        "en": "acidity and stomach problems",
        "te": "అసిడిటీ మరియు కడుపు సమస్యలు",
        "hi": "एसिडिटी और पेट की समस्याएं",
    },

    "cholesterol": {
        "en": "high cholesterol",
        "te": "అధిక కొలెస్ట్రాల్",
        "hi": "उच्च कोलेस्ट्रॉल",
    },

    "supplement": {
        "en": "vitamin or mineral deficiency",
        "te": "విటమిన్ లేదా మినరల్ లోపం",
        "hi": "विटामिन या खनिज की कमी",
    },

    "skin_care": {
        "en": "skin problems",
        "te": "చర్మ సమస్యలు",
        "hi": "त्वचा की समस्याएं",
    },

    "mental_health": {
        "en": "anxiety or mood-related conditions",
        "te": "ఆందోళన లేదా మానసిక సమస్యలు",
        "hi": "चिंता या मानसिक समस्याएं",
    },

    "respiratory": {
        "en": "breathing or cough problems",
        "te": "శ్వాస లేదా దగ్గు సమస్యలు",
        "hi": "सांस या खांसी की समस्याएं",
    },

    "digestive_upset": {
        "en": "nausea, vomiting, or diarrhea",
        "te": "వాంతులు లేదా విరేచనాలు",
        "hi": "उल्टी या दस्त",
    },

    "pain_relief": {
        "en": "pain, fever, or inflammation",
        "te": "నొప్పి, జ్వరం లేదా వాపు",
        "hi": "दर्द, बुखार या सूजन",
    },

    "thyroid": {
        "en": "thyroid problems",
        "te": "థైరాయిడ్ సమస్యలు",
        "hi": "थायरॉइड की समस्या",
    },

    "antiseptic": {
        "en": "wound care",
        "te": "గాయం సంరక్షణ",
        "hi": "घाव की देखभाल",
    },

    "general": {
        "en": "general health purposes",
        "te": "సాధారణ ఆరోగ్య అవసరాలు",
        "hi": "सामान्य स्वास्थ्य आवश्यकताओं",
    },
}


# =========================================================
# WARNING PHRASES
# =========================================================

WARNING_PHRASES = {

    "drowsiness": {
        "en": "It may cause drowsiness, so avoid driving until you know how it affects you.",
        "te": "దీనివల్ల నిద్రమత్తు రావచ్చు. ఇది మీపై ఎలా ప్రభావం చూపుతుందో తెలిసే వరకు వాహనం నడపవద్దు.",
        "hi": "इससे नींद आ सकती है। इसका असर पता चलने तक गाड़ी न चलाएं।",
    },

    "avoid_alcohol": {
        "en": "Avoid alcohol while taking this medicine.",
        "te": "ఈ మందు తీసుకుంటున్నప్పుడు మద్యం నివారించండి.",
        "hi": "यह दवा लेते समय शराब से बचें।",
    },

    "take_with_food": {
        "en": "Take this medicine with food.",
        "te": "ఈ మందును ఆహారంతో తీసుకోండి.",
        "hi": "यह दवा भोजन के साथ लें।",
    },

    "avoid_pregnancy": {
        "en": "Do not use this medicine during pregnancy unless your doctor advises it.",
        "te": "డాక్టర్ సలహా లేకుండా గర్భధారణ సమయంలో ఈ మందును వాడవద్దు.",
        "hi": "डॉक्टर की सलाह के बिना गर्भावस्था में इस दवा का उपयोग न करें।",
    },

    "external_use_only": {
        "en": "For external use only. Do not swallow.",
        "te": "బాహ్య వినియోగానికి మాత్రమే. మింగవద్దు.",
        "hi": "केवल बाहरी उपयोग के लिए। निगलें नहीं।",
    },

    "monitor_kidney": {
        "en": "This medicine may affect kidney function. Regular medical checkups may be advised.",
        "te": "ఈ మందు మూత్రపిండాల పనితీరును ప్రభావితం చేయవచ్చు. క్రమం తప్పకుండా వైద్య పరీక్షలు అవసరం కావచ్చు.",
        "hi": "यह दवा किडनी के कार्य को प्रभावित कर सकती है। नियमित जांच की आवश्यकता हो सकती है।",
    },

    "habit_forming": {
        "en": "This medicine may be habit-forming. Use it only as directed by your doctor.",
        "te": "ఈ మందుకు అలవాటు పడే అవకాశం ఉంది. డాక్టర్ సూచించిన విధంగా మాత్రమే వాడండి.",
        "hi": "यह दवा आदत बना सकती है। केवल डॉक्टर के निर्देशानुसार ही लें।",
    },

    "empty_stomach": {
        "en": "Take this medicine on an empty stomach.",
        "te": "ఈ మందును ఖాళీ కడుపుతో తీసుకోండి.",
        "hi": "यह दवा खाली पेट लें।",
    },

    "do_not_stop_suddenly": {
        "en": "Do not stop taking this medicine suddenly without consulting your doctor.",
        "te": "డాక్టర్‌ను సంప్రదించకుండా ఈ మందును అకస్మాత్తుగా ఆపవద్దు.",
        "hi": "डॉक्टर से सलाह लिए बिना इस दवा को अचानक बंद न करें।",
    },

    "sun_sensitivity": {
        "en": "This medicine may increase sensitivity to sunlight. Use sun protection.",
        "te": "ఈ మందు వల్ల ఎండకు సున్నితత్వం పెరగవచ్చు. సూర్యరశ్మి నుండి రక్షణ తీసుకోండి.",
        "hi": "यह दवा धूप के प्रति संवेदनशीलता बढ़ा सकती है। धूप से बचाव करें।",
    },

    "consult_doctor": {
        "en": "Follow your doctor's instructions carefully.",
        "te": "మీ డాక్టర్ సూచనలను జాగ్రత్తగా పాటించండి.",
        "hi": "अपने डॉक्टर के निर्देशों का सावधानीपूर्वक पालन करें।",
    },
}


# =========================================================
# DOSAGE FREQUENCY PHRASES
# =========================================================

FREQUENCY_PHRASES = {

    "once daily": {
        "te": "రోజుకు ఒకసారి",
        "hi": "दिन में एक बार",
    },

    "twice daily": {
        "te": "రోజుకు రెండుసార్లు",
        "hi": "दिन में दो बार",
    },

    "three times daily": {
        "te": "రోజుకు మూడుసార్లు",
        "hi": "दिन में तीन बार",
    },

    "four times daily": {
        "te": "రోజుకు నాలుగుసార్లు",
        "hi": "दिन में चार बार",
    },

    "as needed": {
        "te": "అవసరమైనప్పుడు",
        "hi": "आवश्यकता अनुसार",
    },

    "with food": {
        "te": "ఆహారంతో",
        "hi": "भोजन के साथ",
    },

    "before meals": {
        "te": "భోజనానికి ముందు",
        "hi": "भोजन से पहले",
    },

    "after food": {
        "te": "భోజనం తర్వాత",
        "hi": "भोजन के बाद",
    },

    "at night": {
        "te": "రాత్రి",
        "hi": "रात को",
    },
}


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(value) -> str:
    """
    Convert database values into clean strings.
    """

    if value is None:
        return ""

    text = str(value).strip()

    if not text:
        return ""

    # Handle pandas NaN values.
    if text.lower() in {
        "nan",
        "none",
        "null",
        "n/a",
        "na",
        "-"
    }:
        return ""

    return text


# =========================================================
# EXTRACT SIDE EFFECTS
# =========================================================

def extract_side_effects(value, limit=4):
    """
    Extract up to four side effects from the database.

    Supports commas, semicolons, and simple 'and' separators.
    """

    text = clean_text(value)

    if not text:
        return []

    # Normalize separators.
    text = text.replace(
        ";",
        ","
    )

    # Split comma-separated values.
    parts = [
        item.strip()
        for item in text.split(",")
        if item.strip()
    ]

    cleaned = []

    for item in parts:

        item = re_cleanup(item)

        if not item:
            continue

        if item not in cleaned:
            cleaned.append(item)

        if len(cleaned) >= limit:
            break

    return cleaned


def re_cleanup(text):
    """
    Small cleanup function for spoken side-effect names.
    """

    text = str(text).strip()

    text = text.replace(
        "  ",
        " "
    )

    return text


# =========================================================
# DOSAGE TRANSLATION
# =========================================================

def translate_dosage(
    dosage_text,
    lang
):
    """
    Translate common English frequency phrases while
    keeping numbers and units unchanged.
    """

    dosage_text = clean_text(
        dosage_text
    )

    if not dosage_text:

        if lang == "te":
            return "డాక్టర్ సూచించిన విధంగా"

        if lang == "hi":
            return "डॉक्टर के निर्देशानुसार"

        return "as directed by your doctor"

    if lang == "en":
        return dosage_text

    result = dosage_text

    for phrase, translations in (
        FREQUENCY_PHRASES.items()
    ):

        if phrase in result.lower():

            result = result.lower().replace(
                phrase,
                translations[lang]
            )

    return result


# =========================================================
# BUILD SENTENCE
# =========================================================

def build_sentence(
    info,
    lang="en"
):
    """
    Build a short, clean and natural spoken summary.

    The sentence contains:
    - Medicine
    - Purpose
    - Dosage
    - Up to four side effects
    - Important warning
    """

    if lang not in {
        "en",
        "te",
        "hi"
    }:

        lang = "en"

    # -----------------------------------------------------
    # MEDICINE NAME
    # -----------------------------------------------------

    name = clean_text(
        info.get(
            "name",
            "Unknown medicine"
        )
    )

    if not name:
        name = "Unknown medicine"

    # -----------------------------------------------------
    # CATEGORY
    # -----------------------------------------------------

    category = clean_text(
        info.get(
            "category",
            "general"
        )
    )

    purpose_data = CATEGORY_PHRASES.get(
        category,
        CATEGORY_PHRASES["general"]
    )

    purpose = purpose_data.get(
        lang,
        purpose_data["en"]
    )

    # -----------------------------------------------------
    # DATABASE PURPOSE
    # -----------------------------------------------------

    database_purpose = clean_text(
        info.get(
            "commonly_used_for",
            ""
        )
    )

    # Prefer the database's actual purpose when present.
    if database_purpose:

        if lang == "en":
            purpose = database_purpose

        elif lang == "te":
            # Keep curated category translation for Telugu
            # rather than machine-translating arbitrary medical text.
            pass

        elif lang == "hi":
            # Keep curated category translation for Hindi.
            pass

    # -----------------------------------------------------
    # DOSAGE
    # -----------------------------------------------------

    dosage = translate_dosage(
        info.get(
            "typical_dosage",
            ""
        ),
        lang
    )

    # -----------------------------------------------------
    # SIDE EFFECTS
    # -----------------------------------------------------

    side_effects = extract_side_effects(
        info.get(
            "common_side_effects",
            ""
        ),
        limit=4
    )

    # -----------------------------------------------------
    # WARNING
    # -----------------------------------------------------

    key_warning = clean_text(
        info.get(
            "key_warning",
            "consult_doctor"
        )
    )

    warning_data = WARNING_PHRASES.get(
        key_warning,
        WARNING_PHRASES["consult_doctor"]
    )

    warning = warning_data.get(
        lang,
        warning_data["en"]
    )

    # =====================================================
    # ENGLISH
    # =====================================================

    if lang == "en":

        sentence = (
            f"{name}. "
            f"This medicine is commonly used for "
            f"{purpose}. "
            f"The usual dose is {dosage}. "
        )

        if side_effects:

            sentence += (
                "Common side effects may include "
                + ", ".join(side_effects)
                + ". "
            )

        sentence += warning

        return sentence

    # =====================================================
    # TELUGU
    # =====================================================

    if lang == "te":

        sentence = (
            f"{name}. "
            f"ఈ మందును {purpose} కోసం ఉపయోగిస్తారు. "
            f"సాధారణ మోతాదు {dosage}. "
        )

        if side_effects:

            sentence += (
                "సాధారణ దుష్ప్రభావాలు "
                + ", ".join(side_effects)
                + ". "
            )

        sentence += warning

        return sentence

    # =====================================================
    # HINDI
    # =====================================================

    sentence = (
        f"{name}। "
        f"इस दवा का उपयोग {purpose} के लिए किया जाता है। "
        f"सामान्य खुराक {dosage} है। "
    )

    if side_effects:

        sentence += (
            "सामान्य दुष्प्रभावों में "
            + ", ".join(side_effects)
            + " शामिल हो सकते हैं। "
        )

    sentence += warning

    return sentence

