"""
translations.py — Curated Telugu/Hindi phrases for drug categories and
common warnings, used to build natural-sounding native-language audio
instead of feeding raw English text into gTTS with a Telugu/Hindi voice.

IMPORTANT: these are best-effort translations, not certified medical
translations. Before this reaches a real user, have a fluent Telugu/Hindi
speaker review the phrasing for accuracy and naturalness.
"""

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
        "en": "allergies",
        "te": "అలర్జీలు",
        "hi": "एलर्जी",
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
        "te": "సాధారణ ఆరోగ్య అవసరాల కోసం",
        "hi": "सामान्य स्वास्थ्य आवश्यकताओं के लिए",
    },
}

WARNING_PHRASES = {
    "drowsiness": {
        "en": "This medicine may cause drowsiness. Do not drive after taking it.",
        "te": "ఈ మందు వల్ల నిద్ర రావచ్చు. దీన్ని తీసుకున్న తర్వాత వాహనం నడపవద్దు.",
        "hi": "यह दवा नींद ला सकती है। इसे लेने के बाद गाड़ी न चलाएं।",
    },
    "avoid_alcohol": {
        "en": "Avoid alcohol while taking this medicine.",
        "te": "ఈ మందు తీసుకుంటున్నప్పుడు మద్యం మానుకోండి.",
        "hi": "यह दवा लेते समय शराब से बचें।",
    },
    "take_with_food": {
        "en": "Take this medicine with food.",
        "te": "ఈ మందును ఆహారంతో తీసుకోండి.",
        "hi": "यह दवा भोजन के साथ लें।",
    },
    "avoid_pregnancy": {
        "en": "Avoid this medicine during pregnancy unless your doctor advises otherwise.",
        "te": "గర్భధారణ సమయంలో డాక్టర్ సలహా లేకుండా ఈ మందు వాడవద్దు.",
        "hi": "गर्भावस्था में डॉक्टर की सलाह के बिना इस दवा से बचें।",
    },
    "external_use_only": {
        "en": "For external use only. Do not swallow.",
        "te": "బాహ్య వినియోగానికి మాత్రమే. మింగవద్దు.",
        "hi": "केवल बाहरी उपयोग के लिए। निगले नहीं।",
    },
    "monitor_kidney": {
        "en": "This medicine may affect kidney function, so regular checkups are advised.",
        "te": "ఈ మందు మూత్రపిండాల పనితీరును ప్రభావితం చేయవచ్చు, కాబట్టి క్రమం తప్పకుండా పరీక్షలు చేయించుకోండి.",
        "hi": "यह दवा किडनी के कार्य को प्रभावित कर सकती है, इसलिए नियमित जांच कराएं।",
    },
    "habit_forming": {
        "en": "This medicine can be habit-forming. Use only as directed by your doctor.",
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
        "te": "డాక్టర్‌ను సంప్రదించకుండా ఈ మందును ఆకస్మికంగా ఆపవద్దు.",
        "hi": "डॉक्टर से सलाह लिए बिना इस दवा को अचानक बंद न करें।",
    },
    "sun_sensitivity": {
        "en": "This medicine may increase sensitivity to sunlight. Use sun protection.",
        "te": "ఈ మందు వల్ల ఎండకు సున్నితత్వం పెరగవచ్చు. సన్‌స్క్రీన్ వాడండి.",
        "hi": "यह दवा धूप के प्रति संवेदनशीलता बढ़ा सकती है। धूप से बचाव करें।",
    },
    "consult_doctor": {
        "en": "Please follow your doctor's instructions carefully for this medicine.",
        "te": "ఈ మందు కోసం మీ డాక్టర్ సూచనలను జాగ్రత్తగా పాటించండి.",
        "hi": "इस दवा के लिए अपने डॉक्टर के निर्देशों का सावधानीपूर्वक पालन करें।",
    },
}


TEMPLATES = {
    "en": "This medicine is {name}. It is commonly used for {purpose}. Typical dosage is {dosage}. {warning}",
    "te": "ఈ మందు {name}. ఇది {purpose} కోసం ఉపయోగిస్తారు. సాధారణ మోతాదు {dosage}. {warning}",
    "hi": "यह दवा {name} है। इसका उपयोग {purpose} के लिए किया जाता है। सामान्य खुराक {dosage} है। {warning}",
}


FREQUENCY_PHRASES = {
    "once daily": {"te": "రోజుకు ఒకసారి", "hi": "दिन में एक बार"},
    "twice daily": {"te": "రోజుకు రెండుసార్లు", "hi": "दिन में दो बार"},
    "three times daily": {"te": "రోజుకు మూడుసార్లు", "hi": "दिन में तीन बार"},
    "as needed": {"te": "అవసరమైనప్పుడు", "hi": "आवश्यकता अनुसार"},
    "with food": {"te": "ఆహారంతో", "hi": "भोजन के साथ"},
    "before meals": {"te": "భోజనానికి ముందు", "hi": "भोजन से पहले"},
    "after food": {"te": "భోజనం తర్వాత", "hi": "भोजन के बाद"},
    "at night": {"te": "రాత్రి", "hi": "रात को"},
}


def translate_dosage(dosage_text, lang):
    """
    Replace known English frequency phrases inside a dosage string with
    their native-language equivalent. Numbers and units (mg, ml) are left
    as-is since they're read correctly by gTTS in any language. Anything
    not in FREQUENCY_PHRASES stays in English as a fallback -- imperfect,
    but better than trying to auto-translate arbitrary medical phrasing.
    """
    if lang == "en":
        return dosage_text
    result = dosage_text
    for phrase, translations in FREQUENCY_PHRASES.items():
        if phrase in result.lower():
            result = result.lower().replace(phrase, translations[lang])
    return result


def build_sentence(info, lang="en"):
    """
    info must have: name, typical_dosage, category, key_warning
    (category/key_warning come from the tagging step, not raw CSV text)
    """
    purpose = CATEGORY_PHRASES.get(info["category"], CATEGORY_PHRASES["general"])[lang]
    warning = WARNING_PHRASES.get(info["key_warning"], WARNING_PHRASES["consult_doctor"])[lang]
    dosage = translate_dosage(info["typical_dosage"], lang)
    return TEMPLATES[lang].format(
        name=info["name"],
        purpose=purpose,
        dosage=dosage,
        warning=warning,
    )
