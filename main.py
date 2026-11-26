import json
import os
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


DATA_FILE = "silpia_data.json"


class SilpiaLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15, **kwargs)
        self.history = []
        self.mode = "active"
        self.load_data()

        self.title_label = Label(
            text="Silpia",
            font_size="32sp",
            size_hint_y=0.18,
        )
        self.add_widget(self.title_label)

        self.output_label = Label(
            text="\n".join(self.history[-6:]) if self.history else "Commands: hello, time, status, sleep, active, clear",
            font_size="18sp",
            text_size=(800, None),
            halign="left",
            valign="top",
            size_hint_y=0.44,
        )
        self.add_widget(self.output_label)

        self.input_box = TextInput(
            hint_text="Type command (hello, time, status, sleep, active, clear)...",
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
            except Exception:
                self.history = []
                self.mode = "active"

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {"history": self.history[-50:], "mode": self.mode},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception:
            pass

    def update_history_view(self):
        recent = self.history[-6:]
        self.output_label.text = "\n".join(recent) if recent else "No history."

    def handle_command(self, instance):
        raw_text = self.input_box.text.strip()
        cmd = raw_text.lower()
        now_str = time.strftime("%H:%M:%S")

        if not cmd:
            reply = f"[{now_str}] Silpia: Please type a command."
        elif cmd == "sleep":
            self.mode = "sleep"
            reply = f"[{now_str}] Silpia: Sleep mode active."
        elif cmd == "active" or cmd == "wake":
            self.mode = "active"
            reply = f"[{now_str}] Silpia: Active mode ready."
        elif self.mode == "sleep":
            reply = f"[{now_str}] Silpia (Sleep): Type 'active' to wake me up."
        elif cmd == "hello" or cmd.startswith("hello "):
            reply = f"[{now_str}] Silpia: Hello! Ready."
        elif "time" in cmd:
            reply = f"[{now_str}] Silpia: Current time is {now_str}"
        elif cmd == "status":
            reply = f"[{now_str}] Silpia: Mode {self.mode}, Core step 4 active."
        elif cmd == "clear":
            self.input_box.text = ""
            self.history = []
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