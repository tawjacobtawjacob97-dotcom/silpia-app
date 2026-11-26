import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class SilpiaLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15, **kwargs)

        self.add_widget(Label(text="Silpia", font_size="28sp", size_hint_y=0.2))

        self.status_label = Label(
            text="UI Ready - Core logic will be added step by step.",
            font_size="18sp",
            size_hint_y=0.35,
        )
        self.add_widget(self.status_label)

        self.input_box = TextInput(
            hint_text="Type here...",
            multiline=False,
            font_size="18sp",
            size_hint_y=0.15,
        )
        self.add_widget(self.input_box)

        btn = Button(text="Send / Test", font_size="20sp", size_hint_y=0.2)
        btn.bind(on_press=self.on_action)
        self.add_widget(btn)

    def on_action(self, instance):
        now = time.strftime("%H:%M:%S")
        user_text = self.input_box.text.strip()
        if user_text:
            self.status_label.text = f"[{now}] Silpia heard: {user_text}"
        else:
            self.status_label.text = f"[{now}] Button clicked - Silpia UI working!"


class SilpiaApp(App):
    def build(self):
        return SilpiaLayout()


if __name__ == "__main__":
    SilpiaApp().run()