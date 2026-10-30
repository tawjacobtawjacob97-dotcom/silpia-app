import speech_recognition as sr
import pyautogui
import time
import os
import datetime
import cv2
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

def save_chat_data(command):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("silpia_data_log.txt", "a", encoding="utf-8") as file:
        file.write(f"[{current_time}] User Command: {command}\n")

def save_custom_knowledge(category, title, description):
    filename = "nishi_dictionary.txt" if category == "nishi" else ("local_traditional_medicines.txt" if category == "medicine" else "silpia_knowledge.txt")
    with open(filename, "a", encoding="utf-8") as file:
        file.write(f"Title: {title} | Content: {description}\n")
    speak("Yeh jankari maine local database mein save kar di hai sir")

def tell_current_date_and_time():
    now = datetime.datetime.now()
    current_date = now.strftime("%A, %d %B %Y")
    current_time_str = now.strftime("%I:%M %p")
    response = f"Aaj {current_date} hai sir aur samay {current_time_str} ho raha hai"
    speak(response)

def check_weather_condition():
    current_month = datetime.datetime.now().month
    if current_month in [10, 11, 12, 1]:
        speak("Bahar kaafi thandi hawa chal rahi hai sir mausam ekdam thanda aur suhana hai")
    else:
        speak("Aaj mausam kaafi garam aur dhoop wala hai sir")

def developer_info():
    speak("Mujhe mere developer Taw Jacob ne design kiya hai sir, Main aapki personal family companion hoon")

def global_knowledge_helper(domain):
    if "engineering" in domain:
        speak("Engineering ek aisi takniki vidya hai sir, jismein naye yantra, software aur structures banaye jaate hain.")
    elif "kanoon" in domain:
        speak("Kanoon desh ke niyamoon ka palan karne aur samaj mein shanti banaye rakhne ke liye hota hai.")
    elif "medical" in domain:
        speak("Medical vigyan human body aur bimariyon ke ilaaj se juda hota hai sir.")
    elif "krishi" in domain:
        speak("Krishi aur pashupalan hamari kheti aur janwaro ki dekhbhal se juda hua mukhya kshetra hai.")
    elif "hacking" in domain:
        speak("Ethical hacking aur cyber security systems ki suraksha aur unke vulnerabilities ko samajhne ki takniki vidya hai sir.")
    else:
        speak(f"Sir {domain} ke bare mein hamari files mein jankari uplabhd hai.")

features_unlocked = False

def listen_command():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Sunte Sunte... (Bolie)")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=None, phrase_time_limit=6)
        
        command = r.recognize_google(audio, language='en-IN')
        print(f"user said: {command}")
        save_chat_data(command)
        return command.lower()
    except Exception:
        return ""

if __name__ == "__main__":
    # Silent startup, waiting for commands directly
    while True:
        query = listen_command()
        if query == "":
            continue
            
        # Direct command processing without extra waiting loops
        if any(w in query for w in ["kaise ho", "kya haal hai", "how are you", "sab theek", "haal"]):
            speak("Main ekdam maze mein hoon sir Bataiye aaj kya karna hai")
        elif any(w in query for w in ["thank you", "shukriya", "dhanyawad", "thank"]):
            speak("Are shukriya kis baat ke liye sir yeh toh mera farz hai")
        elif any(w in query for w in ["unlock", "kholo", "lock kholo"]):
            features_unlocked = True
            speak("Saare security taale khol diye gaye hain sir")
        elif any(w in query for w in ["date", "time", "tariq", "samay", "baj", "time kya"]):
            tell_current_date_and_time()
        elif any(w in query for w in ["weather", "mausam", "thanda", "garmi"]):
            check_weather_condition()
        elif any(w in query for w in ["developer", "who made you", "tumhe kisne banaya", "kaun banaya"]):
            developer_info()
        elif "chinese" in query:
            try:
                speak("Theek hai sir ab typing shuru kar rahi hoon")
                pyautogui.write("[CHINESE]: Nǐ hǎo, wǒ shì Silpia", interval=0.03)
                pyautogui.press('enter')
            except Exception:
                pass
        elif "spanish" in query:
            try:
                speak("Theek hai sir ab typing shuru kar rahi hoon")
                pyautogui.write("[SPANISH]: Hola, soy Silpia", interval=0.03)
                pyautogui.press('enter')
            except Exception:
                pass
        elif "law" in query or "kanoon" in query:
            global_knowledge_helper("kanoon")
        elif "engineer" in query or "tech" in query:
            global_knowledge_helper("engineering")
        elif "medical" in query or "doctor" in query or "bacteria" in query:
            global_knowledge_helper("medical science")
        elif "farming" in query or "animal" in query or "duck" in query:
            global_knowledge_helper("krishi aur pashupalan")
        elif "hacking" in query or "security" in query or "cyber" in query:
            global_knowledge_helper("hacking")
        elif any(w in query for w in ["hello shilpi", "shilpi", "hi shilpi", "shilpa", "silpia"]):
            speak("जी सर, बताइए क्या हुक्म है?")
        else:
            speak("Hukum dijiye sir is command par kya action lena hai")