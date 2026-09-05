from gtts import gTTS

# English
gTTS(text="This medicine is Cetirizine, used for allergies.", lang='en').save('test_en.mp3')

# Hindi
gTTS(text="यह दवा सिटिरिज़िन है, जो एलर्जी के लिए उपयोग की जाती है।", lang='hi').save('test_hi.mp3')

# Telugu
gTTS(text="ఈ మందు సెటిరిజిన్, అలర్జీల కోసం ఉపయోగించబడుతుంది.", lang='te').save('test_te.mp3')

print("Saved all three audio files")