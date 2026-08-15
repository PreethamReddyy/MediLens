import pandas as pd
from rapidfuzz import fuzz, process

df = pd.read_csv('drugs_fixed.csv')

all_names = []
for _, row in df.iterrows():
    all_names.append(row['name'])
    for alias in row['aliases'].split(','):
        all_names.append(alias.strip())

print(f"Total names to match against: {len(all_names)}")

CONFIDENCE_THRESHOLD = 60  # below this, we say "not found" instead of guessing

def lookup(ocr_text):
    best_match, score, _ = process.extractOne(ocr_text, all_names, scorer=fuzz.ratio)
    if score < CONFIDENCE_THRESHOLD:
        print(f"OCR read: '{ocr_text}' -> No confident match found (best guess was '{best_match}' at {score:.1f}%, too low to trust)")
        return None
    print(f"OCR read: '{ocr_text}' -> Matched: '{best_match}' (similarity: {score:.1f}%)")
    return best_match


def get_drug_info(matched_name):
    for _, row in df.iterrows():
        # Check if it matches the main name
        if row['name'].strip().lower() == matched_name.strip().lower():
            return row
        # Check if it matches one of the aliases
        aliases = [a.strip().lower() for a in row['aliases'].split(',')]
        if matched_name.strip().lower() in aliases:
            return row
    return None


def full_lookup(ocr_text):
    matched_name = lookup(ocr_text)
    if matched_name is None:
        return

    info = get_drug_info(matched_name)
    print(f"\n--- Drug Info ---")
    print(f"Name: {info['name']}")
    print(f"Dosage forms: {info['dosage_forms']}")
    print(f"Typical dosage: {info['typical_dosage']}")
    print(f"Commonly used for: {info['commonly_used_for']} (informational only, not a diagnosis)")
    print(f"Warnings: {info['warnings']}")


full_lookup("Okacet")
print()
full_lookup("Cetzte")