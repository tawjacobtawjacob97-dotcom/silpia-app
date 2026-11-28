import json
import os
import time
import speech_recognition as sr
import pyttsx3

ASSISTANT_NAME = "Silpia"
CREATOR_NAME = "ताव जैकूब"
OWNER_NAME = "ताव जैकूब"
NOTES_FILE = "silpia_quick_notes.json"

# बड़े/भारी मॉड्यूल फ़िलहाल बंद (False) रखे गए हैं
FEATURE_FLAGS = {
    "memory_calendar": False,
    "call_message_assistant": False,
    "camera_vision": False,
    "laptop_bridge": False,
}


def init_tts():
    engine = pyttsx3.init()
    engine.setProperty("rate", 165)
    engine.setProperty("volume", 1.0)
    return engine


def speak(engine, text):
    print(f"{ASSISTANT_NAME}: {text}")
    engine.say(text)
    engine.runAndWait()


def load_notes():
    if not os.path.exists(NOTES_FILE):
        return []
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_note(note_text):
    notes = load_notes()
    entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "note": note_text,
    }
    notes.append(entry)
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    return entry


def is_creator_query(text):
    lower = text.lower()
    keywords = [
        "कौन बनाया",
        "किसने बनाया",
        "बनाने वाला",
        "बनाया है",
        "क्रिएटर",
        "creator",
        "made you",
        "created you",
        "मालिक",
        "owner",
        "बॉस",
        "boss",
    ]
    return any(k in text or k in lower for k in keywords)


def listen_upgraded(engine, recognizer, mic, timeout=6, phrase_time_limit=10):
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.6)
        recognizer.pause_threshold = 0.9
        recognizer.dynamic_energy_threshold = True
        try:
            audio = recognizer.listen(
                source, timeout=timeout, phrase_time_limit=phrase_time_limit
            )
        except sr.WaitTimeoutError:
            return None

    try:
        text = recognizer.recognize_google(audio, language="hi-IN")
        return text.strip()
    except sr.UnknownValueError:
        speak(engine, "जी सर, आवाज़ साफ़ नहीं आई, कृपया दोबारा बोलें।")
        return ""
    except sr.RequestError:
        try:
            text = recognizer.recognize_sphinx(audio)
            return text.strip()
        except Exception:
            speak(engine, "जी सर, अभी ऑफ़लाइन वॉइस मॉडल उपलब्ध नहीं है।")
            return ""


def handle_command(engine, text):
    lower = text.lower()

    if any(w in lower for w in ["बंद करो", "रुको", "exit", "quit", "stop"]):
        speak(engine, f"जी सर, {ASSISTANT_NAME} अभी रुक रही है।")
        return False

    # क्रिएटर और मालिक की सीधी व पक्की पहचान
    if is_creator_query(text):
        speak(
            engine,
            f"जी सर, मेरा नाम {ASSISTANT_NAME} है और मेरे क्रिएटर व मालिक {CREATOR_NAME} हैं।",
        )
        return True

    if "नोट" in text or "याद रख" in text or "भूल" in text:
        saved = save_note(text)
        speak(engine, f"जी सर, मैंने यह बात नोट कर ली है: {saved['note']}")
        return True

    if "क्या याद" in text or "क्या नोट" in text or "अधूरा" in text:
        notes = load_notes()
        if not notes:
            speak(engine, "जी सर, अभी कोई हल्का नोट सेव नहीं है।")
        else:
            last = notes[-1]
            speak(engine, f"जी सर, आख़िरी नोट यह है: {last['note']}")
        return True

    if "फीचर" in text or "मॉड्यूल" in text or "स्विच" in text:
        active_list = [k for k, v in FEATURE_FLAGS.items() if v]
        speak(
            engine,
            f"जी सर, बड़े मॉड्यूल फ़िलहाल बंद हैं। सक्रिय मॉड्यूल: {', '.join(active_list) if active_list else 'कोई नहीं'}.",
        )
        return True

    speak(engine, f"जी सर, मैंने सुना: {text}")
    return True


def main():
    engine = init_tts()
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    speak(engine, f"यस सर, {ASSISTANT_NAME} तैयार है। बताइए क्या करना है?")

    running = True
    while running:
        spoken = listen_upgraded(engine, recognizer, mic)
        if spoken:
            running = handle_command(engine, spoken)


if __name__ == "__main__":
    main()