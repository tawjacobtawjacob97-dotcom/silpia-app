from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class SilpiyaUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=24, spacing=16, **kwargs)

        self.title_label = Label(
            text="सिल्पिया (Silpia)",
            font_size="28sp",
            size_hint_y=None,
            height=60,
        )
        self.status_label = Label(
            text="UI तैयार है — अभी कोई भारी लॉजिक नहीं जोड़ा गया है।",
            font_size="16sp",
        )
        self.action_btn = Button(
            text="टेस्ट बटन (UI चेक)",
            font_size="18sp",
            size_hint_y=None,
            height=64,
        )
        self.action_btn.bind(on_press=self.on_button_click)

        self.add_widget(self.title_label)
        self.add_widget(self.status_label)
        self.add_widget(self.action_btn)

    def on_button_click(self, instance):
        self.status_label.text = "बटन काम कर रहा है — UI साफ़ चल रहा है।"


class SilpiyaApp(App):
    def build(self):
        return SilpiyaUI()


if __name__ == "__main__":
    SilpiyaApp().run()