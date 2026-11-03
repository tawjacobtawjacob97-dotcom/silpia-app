import time
import os
from gtts import gTTS
from playsound import playsound

def speak(text):
    print(f"Silpia: {text}")
    try:
        clean_text = text.replace('(', ' ').replace(')', ' ').replace('[', ' ').replace(']', ' ').replace('"', '').replace("'", "")
        tts = gTTS(text=clean_text, lang='hi', slow=False)
        filename = "silpia_voice.mp3"
        if os.path.exists(filename):
            os.remove(filename)
        tts.save(filename)
        playsound(filename)
    except Exception as e:
        print(f"Speech Error: {e}")

if __name__ == "__main__":
    speak("Silpia system active ho gaya hai sir.")
    speak("Ji sar, bataiye kya hukum hai?")