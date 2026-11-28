import json
import os
import time
import urllib.parse
import urllib.request
from kivy.app import App
from kivy.clock import mainthread
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

try:
  from jnius import autoclass, PythonJavaClass, java_method

  ANDROID_AVAILABLE = True
except Exception:
  ANDROID_AVAILABLE = False


if ANDROID_AVAILABLE:

  class SpeechActivityResultListener(PythonJavaClass):
    __javainterfaces__ = ["org/kivy/android/PythonActivity$ActivityResultListener"]
    __javacontext__ = "app"

    def __init__(self, callback):
      super().__init__()
      self.callback = callback

    @java_method("(IILandroid/content/Intent;)V")
    def onActivityResult(self, request_code, result_code, data):
      if self.callback:
        self.callback(request_code, result_code, data)


  class TtsInitListener(PythonJavaClass):
    __javainterfaces__ = ["android/speech/tts/TextToSpeech$OnInitListener"]
    __javacontext__ = "app"

    def __init__(self, on_init_callback):
      super().__init__()
      self.on_init_callback = on_init_callback

    @java_method("(I)V")
    def onInit(self, status):
      if self.on_init_callback:
        self.on_init_callback(status)


class SilpiaAssistantUI(BoxLayout):
  VOICE_REQUEST_CODE = 1001

  def __init__(self, **kwargs):
    super().__init__(orientation="vertical", padding=15, spacing=12, **kwargs)

    self.assistant_name = "Silpia"
    self.creator_name = "Taaw Jacob"
    self.owner_name = "Taaw Jacob"
    self.default_weather_place = "Arunachal Pradesh"
    self.is_awake = True

    self.data_file = "silpia_data.json"
    self.notes_file = "silpia_quick_notes.json"
    self.feature_flags = {
        "memory_calendar": False,
        "call_message_assistant": False,
        "camera_vision": False,
        "laptop_bridge": False,
    }
    self.history = []

    self.tts = None
    self.tts_ready = False
    self._tts_listener = None
    self._result_listener = None
    self._result_listener_registered = False

    self.load_data()
    self.build_ui()
    self.update_history_view()
    self.init_tts()
    self.bind_android_result_listener()

  def build_ui(self):
    self.header_label = Label(
        text=f"{self.assistant_name} [ACTIVE]",
        font_size="26sp",
        size_hint_y=None,
        height=55,
    )
    self.add_widget(self.header_label)

    self.scroll_view = ScrollView(size_hint=(1, 1))
    self.history_label = Label(
        text="",
        font_size="17sp",
        size_hint_y=None,
        text_size=(760, None),
        halign="left",
        valign="top",
    )
    self.history_label.bind(
        texture_size=lambda instance, value: setattr(
            self.history_label, "height", value[1] + 20
        ),
        width=lambda instance, value: setattr(
            self.history_label, "text_size", (value - 20, None)
        ),
    )
    self.scroll_view.add_widget(self.history_label)
    self.add_widget(self.scroll_view)

    self.command_input = TextInput(
        hint_text="Type command or tap Voice Test...",
        font_size="18sp",
        multiline=False,
        size_hint_y=None,
        height=55,
    )
    self.command_input.bind(on_text_validate=self.on_send_command)
    self.add_widget(self.command_input)

    self.send_btn = Button(
        text="Send / Test",
        font_size="20sp",
        size_hint_y=None,
        height=60,
    )
    self.send_btn.bind(on_press=self.on_send_command)
    self.add_widget(self.send_btn)

    self.speak_test_btn = Button(
        text="Test Voice (Hello Sir)",
        font_size="20sp",
        size_hint_y=None,
        height=60,
    )
    self.speak_test_btn.bind(
        on_press=lambda instance: self.speak("Hello Sir")
    )
    self.add_widget(self.speak_test_btn)

    self.voice_btn = Button(
        text="Voice Test (Mic)",
        font_size="20sp",
        size_hint_y=None,
        height=60,
    )
    self.voice_btn.bind(on_press=self.start_voice_input)
    self.add_widget(self.voice_btn)

  def load_data(self):
    if os.path.exists(self.data_file):
      try:
        with open(self.data_file, "r", encoding="utf-8") as f:
          data = json.load(f)
          self.is_awake = data.get("is_awake", True)
          self.history = data.get("history", [])
      except Exception:
        self.is_awake = True
        self.history = []

  def save_data(self):
    try:
      with open(self.data_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "is_awake": self.is_awake,
                "history": self.history[-100:],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    except Exception:
      pass

  def load_notes(self):
    if not os.path.exists(self.notes_file):
      return []
    try:
      with open(self.notes_file, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      return []

  def save_note(self, note_text):
    notes = self.load_notes()
    entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "note": note_text,
    }
    notes.append(entry)
    try:
      with open(self.notes_file, "w", encoding="utf-8") as f:
        json.dump(notes[-100:], f, ensure_ascii=False, indent=2)
    except Exception:
      pass
    return entry

  def get_weather_report(self, place=None):
    target_place = (place or self.default_weather_place).strip()
    try:
      encoded_place = urllib.parse.quote(target_place)
      url = f"https://wttr.in/{encoded_place}?format=3"
      req = urllib.request.Request(url, headers={"User-Agent": "SilpiaApp/1.0"})
      with urllib.request.urlopen(req, timeout=5) as resp:
        raw = resp.read().decode("utf-8", errors="ignore").strip()
        if raw and "<" not in raw:
          return f"Weather: {raw}"
    except Exception:
      pass
    return f"Weather data unavailable right now for {target_place}."

  @mainthread
  def update_history_view(self):
    status_text = "ACTIVE" if self.is_awake else "SLEEPING"
    self.header_label.text = f"{self.assistant_name} [{status_text}]"
    self.history_label.text = "\n".join(self.history[-40:])

  def _on_tts_init(self, status):
    try:
      TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
      Locale = autoclass("java.util.Locale")
      if status == TextToSpeech.SUCCESS and self.tts:
        try:
          self.tts.setLanguage(Locale("en", "IN"))
        except Exception:
          try:
            self.tts.setLanguage(Locale.US)
          except Exception:
            pass
        try:
          self.tts.setSpeechRate(1.1)
          self.tts.setPitch(1.0)
        except Exception:
          pass
        self.tts_ready = True
      else:
        self.tts_ready = False
        self.history.append(
            f"[{time.strftime('%H:%M:%S')}] TTS Init status: {status}"
        )
        self.save_data()
        self.update_history_view()
    except Exception as e:
      self.tts_ready = False
      self.history.append(
          f"[{time.strftime('%H:%M:%S')}] TTS Callback Error: {e}"
      )
      self.save_data()
      self.update_history_view()

  def init_tts(self):
    if not ANDROID_AVAILABLE:
      return
    try:
      PythonActivity = autoclass("org.kivy.android.PythonActivity")
      TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
      self._tts_listener = TtsInitListener(self._on_tts_init)
      self.tts = TextToSpeech(PythonActivity.mActivity, self._tts_listener)
    except Exception as e:
      self.tts = None
      self.tts_ready = False
      self.history.append(f"[{time.strftime('%H:%M:%S')}] TTS Init Error: {e}")
      self.save_data()
      self.update_history_view()

  def speak(self, text):
    if not text or not ANDROID_AVAILABLE:
      return
    try:
      if not self.tts:
        self.init_tts()
      if self.tts:
        TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
        HashMap = autoclass("java.util.HashMap")
        params = HashMap()
        self.tts.speak(str(text), TextToSpeech.QUEUE_FLUSH, params)
    except Exception as e:
      self.history.append(f"[{time.strftime('%H:%M:%S')}] TTS Speak Error: {e}")
      self.save_data()
      self.update_history_view()

  def bind_android_result_listener(self):
    if not ANDROID_AVAILABLE or self._result_listener_registered:
      return
    try:
      PythonActivity = autoclass("org.kivy.android.PythonActivity")
      self._result_listener = SpeechActivityResultListener(
          self._on_android_activity_result
      )
      PythonActivity.mActivity.registerActivityResultListener(
          self._result_listener
      )
      self._result_listener_registered = True
    except Exception as e:
      self.history.append(
          f"[{time.strftime('%H:%M:%S')}] Listener Bind Error: {e}"
      )
      self.save_data()
      self.update_history_view()

  def start_voice_input(self, instance=None):
    if not ANDROID_AVAILABLE:
      self.history.append(
          f"[{time.strftime('%H:%M:%S')}] Voice input works on Android APK."
      )
      self.save_data()
      self.update_history_view()
      return

    self.bind_android_result_listener()
    try:
      PythonActivity = autoclass("org.kivy.android.PythonActivity")
      Intent = autoclass("android.content.Intent")
      RecognizerIntent = autoclass("android.speech.RecognizerIntent")

      intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
      intent.putExtra(
          RecognizerIntent.EXTRA_LANGUAGE_MODEL,
          RecognizerIntent.LANGUAGE_MODEL_FREE_FORM,
      )
      intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "hi-IN")
      intent.putExtra(
          RecognizerIntent.EXTRA_PROMPT, f"Speak to {self.assistant_name}..."
      )

      PythonActivity.mActivity.startActivityForResult(
          intent, self.VOICE_REQUEST_CODE
      )
    except Exception as e:
      self.history.append(
          f"[{time.strftime('%H:%M:%S')}] Voice Launch Error: {e}"
      )
      self.save_data()
      self.update_history_view()

  @mainthread
  def _on_android_activity_result(self, request_code, result_code, data):
    if request_code != self.VOICE_REQUEST_CODE:
      return
    try:
      Activity = autoclass("android.app.Activity")
      RecognizerIntent = autoclass("android.speech.RecognizerIntent")
      if result_code == Activity.RESULT_OK and data is not None:
        results = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
        if results and results.size() > 0:
          spoken_text = str(results.get(0))
          self.history.append(f"Voice: {spoken_text}")
          self.process_command(spoken_text)
    except Exception as e:
      self.history.append(
          f"[{time.strftime('%H:%M:%S')}] Voice Result Error: {e}"
      )
      self.save_data()
      self.update_history_view()

  def is_creator_query(self, cmd):
    keywords = [
        "who creat",
        "who create",
        "who created",
        "who made",
        "creat you",
        "create you",
        "created you",
        "made you",
        "creator",
        "owner",
        "boss",
        "kisne banaya",
        "kaun banaya",
        "malik",
    ]
    return any(k in cmd for k in keywords)

  def on_send_command(self, instance=None):
    text = self.command_input.text.strip()
    if not text:
      return
    self.command_input.text = ""
    self.history.append(f"You: {text}")
    self.process_command(text)

  def process_command(self, raw_text):
    cmd = raw_text.strip().lower()
    now_str = time.strftime("%H:%M:%S")
    today_date_str = time.strftime("%d %B %Y (%A)")
    current_month_str = time.strftime("%B (%m)")
    current_year_str = time.strftime("%Y")

    if any(
        w in cmd
        for w in [
            "wake up",
            "wakeup",
            "utho",
            "jag jao",
            "active",
            "yes sir",
        ]
    ):
      self.is_awake = True
      reply = "Yes Sir"
    elif any(w in cmd for w in ["sleep", "so jao", "sleep mode", "sojao"]):
      self.is_awake = False
      reply = "Sleep mode on"
    elif self.is_creator_query(cmd):
      reply = (
          f"Yes Sir, my name is {self.assistant_name} and my creator and owner"
          f" is {self.creator_name}."
      )
    elif "weather" in cmd or "mausam" in cmd or "mosam" in cmd:
      place = None
      if " in " in cmd:
        place = raw_text.split(" in ", 1)[1].strip()
      reply = self.get_weather_report(place)
    elif "month" in cmd or "mahina" in cmd:
      reply = f"Current month is {current_month_str}."
    elif "year" in cmd or "saal" in cmd:
      reply = f"Current year is {current_year_str}."
    elif "date" in cmd or "tarikh" in cmd or "aaj" in cmd or cmd == "death":
      reply = f"Today's date is {today_date_str}."
    elif "note" in cmd or "yaad rakh" in cmd:
      saved = self.save_note(raw_text)
      reply = f"Note saved: {saved['note']}"
    elif "notes" in cmd or "kya yaad" in cmd:
      notes = self.load_notes()
      if not notes:
        reply = "No quick notes saved yet."
      else:
        reply = f"Last note: {notes[-1]['note']}"
    elif "feature" in cmd or "module" in cmd:
      active = [k for k, v in self.feature_flags.items() if v]
      reply = (
          "Heavy modules off. Active:"
          f" {', '.join(active) if active else 'None'}."
      )
    elif "hello" in cmd or "hi" in cmd:
      reply = "Hello Sir"
    elif "namaste" in cmd or "namaskar" in cmd:
      reply = "Namaste Sir"
    elif "time" in cmd or "samay" in cmd:
      reply = f"Current time is {now_str}."
    else:
      if not self.is_awake:
        reply = "Sleeping. Say wake up."
      else:
        reply = f"Heard: {raw_text}"

    self.history.append(f"[{now_str}] {self.assistant_name}: {reply}")
    self.save_data()
    self.update_history_view()
    self.speak(reply)


class SilpiaApp(App):

  def build(self):
    self.title = "Silpia"
    return SilpiaAssistantUI()


if __name__ == "__main__":
  SilpiaApp().run()