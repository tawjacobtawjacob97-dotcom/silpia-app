import json
import os
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


DATA_FILE = "silpia_data.json"
CREATOR_NAME = "ताव जैकूब"
CREATED_DATE = "2026-11-26"

WAKE_PHRASES = (
    "शिल्पी जाग जाओ",
    "सिल्पिया जाग जाओ",
    "जाग जाओ",
    "silpia wake up",
    "wake up",
    "wake",
    "active",
)
SLEEP_PHRASES = (
    "शिल्पी सो जाओ",
    "सिल्पिया सो जाओ",
    "सो जाओ",
    "sleep mode",
    "go to sleep",
    "sleep",
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
        self.load_data()
        self.save_data()

        self.title_label = Label(
            text=f"Silpia  [{self.mode.upper()}]",
            font_size="30sp",
            size_hint_y=0.18,
        )
        self.add_widget(self.title_label)

        self.output_label = Label(
            text="\n".join(self.history[-6:]) if self.history else "Commands: hello, time, status, creator, sleep, शिल्पी जाग जाओ, clear",
            font_size="18sp",
            text_size=(800, None),
            halign="left",
            valign="top",
            size_hint_y=0.44,
        )
        self.add_widget(self.output_label)

        self.input_box = TextInput(
            hint_text="Type command or 'शिल्पी जाग जाओ'...",
            multiline=False,
            font_size="22sp",
            size_hint_y=0.18,
        )
        self.add_widget(self.input_box)

        self.send_button = Button(
            text="Send / Test",
            font_size="24sp",
            size_hint_y=0.2,
        )
        self.send_button.bind(on_press=self.handle_command)
        self.add_widget(self.send_button)

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
                        if isinstance(data.get("creator"), str) and data["creator"].strip():
                            self.creator = data["creator"].strip()
                        if isinstance(data.get("created_date"), str) and data["created_date"].strip():
                            self.created_date = data["created_date"].strip()
            except Exception:
                self.history = []
                self.mode = "active"
                self.sleep_ignored_count = 0
                self.last_mode_change = time.strftime("%Y-%m-%d %H:%M:%S")
                self.creator = CREATOR_NAME
                self.created_date = CREATED_DATE

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "history": self.history[-50:],
                        "mode": self.mode,
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
        self.title_label.text = f"Silpia  [{self.mode.upper()}]"

    def update_history_view(self):
        recent = self.history[-6:]
        self.output_label.text = "\n".join(recent) if recent else "No history."

    def matches_phrases(self, raw_text, cmd, phrases):
        return any(phrase in raw_text or phrase in cmd for phrase in phrases)

    def handle_command(self, instance):
        raw_text = self.input_box.text.strip()
        cmd = raw_text.lower()
        now_str = time.strftime("%H:%M:%S")
        full_now = time.strftime("%Y-%m-%d %H:%M:%S")

        if not raw_text:
            reply = f"[{now_str}] Silpia: Please enter a command."
        elif self.matches_phrases(raw_text, cmd, SLEEP_PHRASES):
            self.mode = "sleep"
            self.sleep_ignored_count = 0
            self.last_mode_change = full_now
            self.update_mode_header()
            reply = f"[{now_str}] Silpia: Sleep mode ON. Say 'शिल्पी जाग जाओ' to wake me."
        elif self.matches_phrases(raw_text, cmd, WAKE_PHRASES):
            was_sleeping = self.mode == "sleep"
            self.mode = "active"
            self.sleep_ignored_count = 0
            self.last_mode_change = full_now
            self.update_mode_header()
            if was_sleeping:
                reply = f"[{now_str}] Silpia: जाग गई! Active mode is now ON."
            else:
                reply = f"[{now_str}] Silpia: Already ACTIVE and ready."
        elif self.mode == "sleep":
            self.sleep_ignored_count += 1
            reply = f"[{now_str}] Silpia (Sleep #{self.sleep_ignored_count}): Quiet... say 'शिल्पी जाग जाओ'."
        elif cmd == "hello" or cmd.startswith("hello "):
            reply = f"[{now_str}] Silpia: नमस्ते {self.creator}! मैं तैयार हूँ।"
        elif "time" in cmd or "समय" in raw_text:
            reply = f"[{now_str}] Silpia: अभी का समय {now_str} है।"
        elif (
            "creator" in cmd
            or "बनाया" in raw_text
            or "तारीख" in raw_text
            or "कब बनी" in raw_text
            or "किसने" in raw_text
        ):
            reply = (
                f"[{now_str}] Silpia: मुझे {self.creator} ने बनाया है, "
                f"और मेरी बनने की तारीख {self.created_date} है।"
            )
        elif cmd == "status":
            reply = (
                f"[{now_str}] Silpia: Creator = {self.creator}, Created = {self.created_date}, "
                f"Mode = {self.mode}, Sleep count = {self.sleep_ignored_count}, Since = {self.last_mode_change}."
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

        self.history.append(f"You: {raw_text}")
        self.history.append(reply)
        self.save_data()
        self.input_box.text = ""
        self.update_history_view()


class SilpiaApp(App):
    def build(self):
        return SilpiaLayout()


if __name__ == "__main__":
    SilpiaApp().run()