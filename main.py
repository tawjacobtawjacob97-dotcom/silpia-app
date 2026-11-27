import time
import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import mainthread

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


class SilpiaAssistantUI(BoxLayout):
    VOICE_REQUEST_CODE = 1001

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=15, spacing=12, **kwargs)

        self.assistant_name = "Silpia"
        self.creator_name = "Taaw Jacob"
        self.is_awake = True
        self.data_file = "silpia_data.json"
        self.history = []

        self.tts = None
        self.tts_ready = False
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
            texture_size=lambda instance, value: setattr(self.history_label, "height", value[1] + 20),
            width=lambda instance, value: setattr(self.history_label, "text_size", (value - 20, None)),
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
            height=65,
        )
        self.send_btn.bind(on_press=self.on_send_command)
        self.add_widget(self.send_btn)

        self.voice_btn = Button(
            text="Voice Test (Mic)",
            font_size="20sp",
            size_hint_y=None,
            height=65,
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

    @mainthread
    def update_history_view(self):
        status_text = "ACTIVE" if self.is_awake else "SLEEPING"
        self.header_label.text = f"{self.assistant_name} [{status_text}]"
        self.history_label.text = "\n".join(self.history[-40:])

    def init_tts(self):
        if not ANDROID_AVAILABLE:
            return
        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
            Locale = autoclass("java.util.Locale")

            self.tts = TextToSpeech(PythonActivity.mActivity, None)
            try:
                self.tts.setLanguage(Locale.US)
            except Exception:
                pass
            try:
                self.tts.setSpeechRate(1.15)
                self.tts.setPitch(1.0)
            except Exception:
                pass
            self.tts_ready = True
        except Exception as e:
            self.tts = None
            self.tts_ready = False
            self.history.append(f"[{time.strftime('%H:%M:%S')}] TTS Init Error: {e}")
            self.save_data()
            self.update_history_view()

    def speak(self, text):
        if not text:
            return
        if not ANDROID_AVAILABLE:
            return
        try:
            if not self.tts:
                self.init_tts()
            if self.tts:
                TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
                self.tts.speak(str(text), TextToSpeech.QUEUE_FLUSH, None, None)
        except Exception as e:
            self.history.append(f"[{time.strftime('%H:%M:%S')}] TTS Speak Error: {e}")
            self.save_data()
            self.update_history_view()

    def bind_android_result_listener(self):
        if not ANDROID_AVAILABLE or self._result_listener_registered:
            return
        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            self._result_listener = SpeechActivityResultListener(self._on_android_activity_result)
            PythonActivity.mActivity.registerActivityResultListener(self._result_listener)
            self._result_listener_registered = True
        except Exception as e:
            self.history.append(f"[{time.strftime('%H:%M:%S')}] Listener Bind Error: {e}")
            self.save_data()
            self.update_history_view()

    def start_voice_input(self, instance=None):
        if not ANDROID_AVAILABLE:
            self.history.append(f"[{time.strftime('%H:%M:%S')}] Voice input works on Android APK.")
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
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-IN")
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT, f"Speak to {self.assistant_name}...")

            PythonActivity.mActivity.startActivityForResult(intent, self.VOICE_REQUEST_CODE)
        except Exception as e:
            self.history.append(f"[{time.strftime('%H:%M:%S')}] Voice Launch Error: {e}")
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
            self.history.append(f"[{time.strftime('%H:%M:%S')}] Voice Result Error: {e}")
            self.save_data()
            self.update_history_view()

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

        if any(w in cmd for w in ["wake up", "wakeup", "utho", "jag jao"]):
            self.is_awake = True
            reply = "Yes Sir"
        elif any(w in cmd for w in ["sleep", "so jao", "sleep mode"]):
            self.is_awake = False
            reply = "Sleep mode on"
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