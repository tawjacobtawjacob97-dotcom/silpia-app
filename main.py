import json
import os
import threading
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

try:
    from jnius import autoclass
    from android import activity
    ANDROID_AVAILABLE = True
except Exception:
    autoclass = None
    activity = None
    ANDROID_AVAILABLE = False

DATA_FILE = "silpia_data.json"
CREATOR_NAME = "Taw Jacob"
CREATED_DATE = "2026-11-26"

WAKE_PHRASES = (
    "silpia wake up",
    "shilpi wake up",
    "wake up",
    "wake",
    "active",
    "जाग जाओ",
)

SLEEP_PHRASES = (
    "silpia sleep",
    "go to sleep",
    "sleep mode",
    "sleep",
    "सो जाओ",
)


class SilpiaLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15, **kwargs)
        self.history = []
        self.mode = "active"
        self.sleep_ignored_count = 0
        self.last_mode_change = time.strftime("%Y-%m-%d %H:%M:%S")
        self.creator = CREATOR_NAME
        self.created_date = CREATED_DATE
        self.is_listening = False
        self.load_data()
        self.save_data()

        self.title_label = Label(
            text=f"Silpia [{self.mode.upper()}]",
            font_size="28sp",
            size_hint_y=0.14,
        )
        self.add_widget(self.title_label)

        self.output_label = Label(
            text="\n".join(self.history[-6:])
            if self.history
            else f"Creator: {self.creator} | Date: {self.created_date}\nCommands: hello, time, status, sleep, wake up, clear",
            font_size="18sp",
            text_size=(800, None),
            halign="left",
            valign="top",
            size_hint_y=0.44,
        )
        self.add_widget(self.output_label)

        self.input_box = TextInput(
            hint_text="Type command or tap Voice Test...",
            multiline=False,
            font_size="20sp",
            size_hint_y=0.14,
        )
        self.add_widget(self.input_box)

        self.send_button = Button(
            text="Send / Test",
            font_size="22sp",
            size_hint_y=0.14,
        )
        self.send_button.bind(on_press=self.handle_command)
        self.add_widget(self.send_button)

        self.voice_button = Button(
            text="Voice Test (Mic)",
            font_size="22sp",
            size_hint_y=0.14,
        )
        self.voice_button.bind(on_press=self.start_voice_test)
        self.add_widget(self.voice_button)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    if isinstance(data.get("history"), list):
                        self.history = data["history"]
                    if data.get("mode") in ("active", "sleep"):
                        self.mode = data["mode"]
                    if isinstance(data.get("sleep_ignored_count"), int):
                        self.sleep_ignored_count = data["sleep_ignored_count"]
                    if isinstance(data.get("last_mode_change"), str):
                        self.last_mode_change = data["last_mode_change"]
                    if isinstance(data.get("created_date"), str) and data["created_date"].strip():
                        self.created_date = data["created_date"].strip()
            except Exception:
                self.history = []
                self.mode = "active"
                self.sleep_ignored_count = 0
                self.last_mode_change = time.strftime("%Y-%m-%d %H:%M:%S")
        self.creator = CREATOR_NAME

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "history": self.history[-50:],
                        "sleep_ignored_count": self.sleep_ignored_count,
                        "last_mode_change": self.last_mode_change,
                        "creator": self.creator,
                        "created_date": self.created_date,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception:
            pass

    def update_mode_header(self):
        self.title_label.text = f"Silpia [{self.mode.upper()}]"

    def update_history_view(self):
        recent = self.history[-6:]
        self.output_label.text = "\n".join(recent) if recent else "No history."

    def matches_phrases(self, raw_text, cmd, phrases):
        return any(phrase in raw_text or phrase in cmd for phrase in phrases)

    def process_text(self, raw_text, source="You"):
        raw_text = raw_text.strip()
        cmd = raw_text.lower()
        now_str = time.strftime("%H:%M:%S")
        full_now = time.strftime("%Y-%m-%d %H:%M:%S")

        if not raw_text:
            reply = f"[{now_str}] Silpia: Please enter or say a command."
        elif self.matches_phrases(raw_text, cmd, SLEEP_PHRASES):
            self.mode = "sleep"
            self.sleep_ignored_count = 0
            self.last_mode_change = full_now
            self.update_mode_header()
            reply = f"[{now_str}] Silpia: Sleep mode ON. Say 'wake up' to wake me."
        elif self.matches_phrases(raw_text, cmd, WAKE_PHRASES):
            was_sleeping = self.mode == "sleep"
            self.mode = "active"
            self.sleep_ignored_count = 0
            self.last_mode_change = full_now
            self.update_mode_header()
            if was_sleeping:
                reply = f"[{now_str}] Silpia: Yes Sir! Active mode is now ON."
            else:
                reply = f"[{now_str}] Silpia: Yes Sir, already ACTIVE and ready."
        elif self.mode == "sleep":
            self.sleep_ignored_count += 1
            reply = f"[{now_str}] Silpia (Sleep #{self.sleep_ignored_count}): Quiet..."
        elif cmd == "hello" or cmd.startswith("hello ") or "hi silpia" in cmd:
            reply = f"[{now_str}] Silpia: Hello {self.creator}! Yes Sir, I am ready."
        elif "time" in cmd:
            reply = f"[{now_str}] Silpia: Current time is {now_str}."
        elif (
            "creator" in cmd
            or "creater" in cmd
            or "date" in cmd
            or "who made" in cmd
            or "created" in cmd
        ):
            reply = (
                f"[{now_str}] Silpia: My creator is {self.creator}, "
                f"and my creation date is {self.created_date}."
            )
        elif cmd == "status":
            reply = (
                f"[{now_str}] Silpia: Creator = {self.creator}, Date = {self.created_date}, "
                f"Mode = {self.mode}, Sleep count = {self.sleep_ignored_count}."
            )
        elif cmd == "clear":
            self.input_box.text = ""
            self.history = []
            self.sleep_ignored_count = 0
            self.save_data()
            self.output_label.text = f"[{now_str}] Silpia: History cleared."
            return
        else:
            reply = f"[{now_str}] Silpia heard: {raw_text}"

        self.history.append(f"{source}: {raw_text}")
        self.history.append(reply)
        self.save_data()
        self.input_box.text = ""
        self.update_history_view()

    def handle_command(self, instance):
        self.process_text(self.input_box.text, source="You")

    def start_voice_test(self, instance):
        if self.is_listening:
            return

        now_str = time.strftime("%H:%M:%S")

        if not ANDROID_AVAILABLE:
            self.history.append(
                f"[{now_str}] Silpia: Android voice is only available inside the Android APK."
            )
            self.save_data()
            self.update_history_view()
            return

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
                RecognizerIntent.EXTRA_PROMPT, "Silpia सुन रही है... बोलिए"
            )

            self.is_listening = True
            self.voice_button.text = "Listening..."

            def on_activity_result(request_code, result_code, data):
                if request_code != 1001:
                    return
                try:
                    activity.unbind(on_activity_result=on_activity_result)
                except Exception:
                    pass

                spoken_text = None
                error_msg = "Could not hear clearly"

                try:
                    Activity = autoclass("android.app.Activity")
                    if result_code == Activity.RESULT_OK and data is not None:
                        results = data.getStringArrayListExtra(
                            RecognizerIntent.EXTRA_RESULTS
                        )
                        if results and results.size() > 0:
                            spoken_text = str(results.get(0))
                except Exception as e:
                    error_msg = str(e)

                Clock.schedule_once(
                    lambda dt: self._finish_voice(spoken_text, error_msg), 0
                )

            activity.bind(on_activity_result=on_activity_result)
            current_activity = PythonActivity.mActivity
            current_activity.startActivityForResult(intent, 1001)

        except Exception as e:
            self.is_listening = False
            self.voice_button.text = "Voice Test (Mic)"
            self.history.append(f"[{now_str}] Silpia Voice Error: {e}")
            self.save_data()
            self.update_history_view()

    def _finish_voice(self, spoken_text, error_msg):
        self.is_listening = False
        self.voice_button.text = "Voice Test (Mic)"
        now_str = time.strftime("%H:%M:%S")
        if spoken_text:
            self.process_text(spoken_text, source="Voice")
        else:
            self.history.append(
                f"[{now_str}] Silpia Voice Error: {error_msg or 'Could not hear'}"
            )
            self.save_data()
            self.update_history_view()


class SilpiaApp(App):
    def build(self):
        return SilpiaLayout()


if __name__ == "__main__":
    SilpiaApp().run()