import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class SilpiaLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15, **kwargs)

        self.title_label = Label(
            text="Silpia",
            font_size="32sp",
            size_hint_y=0.2,
        )
        self.add_widget(self.title_label)

        self.output_label = Label(
            text="Commands: hello, time, status, clear",
            font_size="20sp",
            text_size=(800, None),
            halign="center",
            valign="middle",
            size_hint_y=0.4,
        )
        self.add_widget(self.output_label)

        self.input_box = TextInput(
            hint_text="Type command (hello, time, status, clear)...",
            multiline=False,
            font_size="22sp",
            size_hint_y=0.2,
        )
        self.add_widget(self.input_box)

        self.send_button = Button(
            text="Send / Test",
            font_size="24sp",
            size_hint_y=0.2,
        )
        self.send_button.bind(on_press=self.handle_command)
        self.add_widget(self.send_button)

    def handle_command(self, instance):
        raw_text = self.input_box.text.strip()
        cmd = raw_text.lower()
        now_str = time.strftime("%H:%M:%S")

        if not cmd:
            reply = f"[{now_str}] Silpia: Please type a command."
        elif cmd == "hello" or cmd.startswith("hello "):
            reply = f"[{now_str}] Silpia: Hello! Ready."
        elif "time" in cmd:
            reply = f"[{now_str}] Silpia: Current time is {now_str}"
        elif cmd == "status":
            reply = f"[{now_str}] Silpia: Core step 1 active."
        elif cmd == "clear":
            self.input_box.text = ""
            self.output_label.text = f"[{now_str}] Silpia: Screen cleared."
            return
        else:
            reply = f"[{now_str}] Silpia heard: {raw_text}"

        self.output_label.text = reply


class SilpiaApp(App):
    def build(self):
        return SilpiaLayout()


if __name__ == "__main__":
    SilpiaApp().run()