import time
import os
from gtts import gTTS
from kivy.core.audio import SoundLoader

def speak(text):
    print(f"Silpia: {text}")
    try:
        clean_text = text.replace('(', ' ').replace(')', ' ').replace('[', ' ')
        tts = gTTS(text=clean_text, lang='hi', slow=False)
        filename = "silpia_voice.mp3"
        if os.path.exists(filename):
            os.remove(filename)
        tts.save(filename)
        
        # एंड्रॉइड और पीसी दोनों के लिए Kivy SoundLoader का उपयोग
        sound = SoundLoader.load(filename)
        if sound:
            sound.play()
    except Exception as e:
        print(f"Speech Error: {e}")

if __name__ == "__main__":
    speak("Silpia system active ho gaya hai sir.")
    speak("सर, बताइए क्या हुक्म है?")