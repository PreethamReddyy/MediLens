import pandas as pd
from translations import build_sentence
from gtts import gTTS
from playsound import playsound

df = pd.read_csv('drugs_tagged.csv')
row = df[df['name'] == 'Cetirizine'].iloc[0]
info = {
    'name': row['name'],
    'typical_dosage': row['typical_dosage'],
    'category': row['category'],
    'key_warning': row['key_warning'],
}

for lang in ['en', 'te', 'hi']:
    sentence = build_sentence(info, lang)
    print(f"--- {lang} ---")
    print(sentence)
    gTTS(text=sentence, lang=lang).save(f'test_{lang}.mp3')