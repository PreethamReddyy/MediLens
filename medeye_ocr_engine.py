import easyocr
import pandas as pd
from rapidfuzz import fuzz, process

# ---- Manufacturer filter ----
KNOWN_MANUFACTURERS = {
    'cipla', 'sun pharma', 'cadila', 'dr reddy', 'lupin', 'zydus',
    'mankind', 'alkem', 'torrent', 'glenmark', 'abbott', 'gsk'
}

def is_manufacturer(text):
    return text.strip().lower() in KNOWN_MANUFACTURERS

# ---- Load drug database ----
df = pd.read_csv('drugs_fixed.csv')

all_names = []
for _, row in df.iterrows():
    all_names.append(row['name'])
    for alias in row['aliases'].split(','):
        all_names.append(alias.strip())

CONFIDENCE_THRESHOLD = 60

def lookup(ocr_text):
    best_match, score, _ = process.extractOne(ocr_text, all_names, scorer=fuzz.ratio)
    if score < CONFIDENCE_THRESHOLD:
        return None
    return best_match

def get_drug_info(matched_name):
    for _, row in df.iterrows():
        if row['name'].strip().lower() == matched_name.strip().lower():
            return row
        aliases = [a.strip().lower() for a in row['aliases'].split(',')]
        if matched_name.strip().lower() in aliases:
            return row
    return None

def full_lookup(ocr_text):
    matched_name = lookup(ocr_text)
    if matched_name is None:
        print(f"'{ocr_text}' -> No confident match found.")
        return
    info = get_drug_info(matched_name)
    print(f"\n--- Drug Info (from OCR text: '{ocr_text}') ---")
    print(f"Name: {info['name']}")
    print(f"Dosage forms: {info['dosage_forms']}")
    print(f"Typical dosage: {info['typical_dosage']}")
    print(f"Commonly used for: {info['commonly_used_for']} (informational only, not a diagnosis)")
    print(f"Warnings: {info['warnings']}")

# ---- Run OCR on the photo ----
reader = easyocr.Reader(['en'])
result = reader.readtext('med3.jpeg')

OCR_CONFIDENCE_THRESHOLD = 0.5

print("--- High-confidence OCR readings ---")
for detection in result:
    text = detection[1]
    confidence = detection[2]
    if confidence >= OCR_CONFIDENCE_THRESHOLD:
        if is_manufacturer(text):
            print(f"'{text}' -> Skipped (known manufacturer name, not a drug)")
            continue
        print(f"'{text}'  (OCR confidence: {confidence:.2f})")
        full_lookup(text)