import time
import os
from gtts import gTTS
from playsound import playsound

def speak(text):
    print(f"Silpia: {text}")
    try:
        clean_text = text.replace('(', ' ').replace(')', ' ').replace('[', ' ').replace(']', ' ').replace('"', '').replace("'", "")
        tts = gTTS(text=clean_text, lang='hi', slow=False)
        
        # हर बार एक नया यूनिक फाइल नाम बनाएं ताकि पुराना फाइल लॉक न हो
        filename = f"silpia_voice_{int(time.time())}.mp3"
        
        tts.save(filename)
        playsound(filename)
        
        # ऑडियो बजने के बाद फाइल को डिलीट करने की कोशिश करें
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass
            
    except Exception as e:
        print(f"Speech Error: {e}")

if __name__ == '__main__':
    speak("Silpia system active ho gaya hai sir.")
    speak("Ji sar, bataiye kya hukum hai?")
```[cite: 5]

इस कोड को आप अपनी **`silpia.py`** फाइल में सीधे कॉपी और पेस्ट कर सकते हैं[cite: 5]।
