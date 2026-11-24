from kivy.app import App
from kivy.uix.boxlayout import BoxLayout


class SilpiyaApp(App):
    def build(self):
        # अभी एकदम खाली डिब्बा (Empty Box)
        return BoxLayout()


if __name__ == "__main__":
    SilpiyaApp().run()