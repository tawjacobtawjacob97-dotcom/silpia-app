import json
import os
import re
import ssl
import threading
import urllib.parse
import urllib.request
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

CREATOR_NAME = "Taaw Jacob"
ASSISTANT_NAME = "Silpia"

ARUNACHAL_DISTRICTS = [
    "Anjaw",
    "Bichom",
    "Changlang",
    "Dibang Valley",
    "East Kameng",
    "East Siang",
    "Kamle",
    "Keyi Panyor",
    "Kra Daadi",
    "Kurung Kumey",
    "Lepa Rada",
    "Lohit",
    "Longding",
    "Lower Dibang Valley",
    "Lower Siang",
    "Lower Subansiri",
    "Namsai",
    "Pakke-Kessang",
    "Papum Pare",
    "Shi Yomi",
    "Siang",
    "Tawang",
    "Tirap",
    "Upper Siang",
    "Upper Subansiri",
    "West Kameng",
    "West Siang",
    "Itanagar",
]

PRONUNCIATION_REPLACEMENTS = [
    # Keyi Panyor variations
    (
        r"\b(k\s*punjab|punjab|kai\s*panyar|kai\s*panjar|kai\s*panjiyar|kai\s*paneer|kai\s*panir|key\s*panyor|keyi\s*panyor|kei\s*panyor|keyi\s*panior|kayi\s*panyor)\b",
        "keyi panyor",
    ),
    # Papum Pare variations
    (
        r"\b(papampara|papumpare|papum\s*para|papam\s*pare|papum\s*pare)\b",
        "papum pare",
    ),
    # Kurung Kumey variations
    (
        r"\b(kurung\s*kumai|kurung\s*kumey|krunku|kurung)\b",
        "kurung kumey",
    ),
    # Common command pronunciation fixes
    (r"\b(death|det)\b", "date"),
    (r"\b(bed\s*weather|wether|mosam|mausam)\b", "weather"),
    (r"\b(creat|create\s+you)\b", "created you"),
    (r"\b(batri|battery\s+status)\b", "battery"),
    (r"\b(last\s+not|latest\s+note|last\s+note)\b", "last note"),
]


def get_storage_dir() -> str:
    try:
        from android.storage import app_storage_path

        path = app_storage_path()
        if path:
            os.makedirs(path, exist_ok=True)
            return path
    except Exception:
        pass
    return os.path.dirname(os.path.abspath(__file__))


STORAGE_DIR = get_storage_dir()
DATA_FILE = os.path.join(STORAGE_DIR, "silpia_data.json")
NOTES_FILE = os.path.join(STORAGE_DIR, "silpia_quick_notes.json")


def load_json(filepath: str, default):
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def save_json(filepath: str, data) -> None:
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def normalize_command(text: str) -> str:
    if not text:
        return ""
    cleaned = text.lower().strip()
    for pattern, replacement in PRONUNCIATION_REPLACEMENTS:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_weather_location(normalized_text: str) -> str:
    for dist in ARUNACHAL_DISTRICTS:
        if re.search(rf"\b{re.escape(dist.lower())}\b", normalized_text):
            return dist

    match = re.search(
        r"(?:weather\s+(?:of|in|for|at)?\s+|of\s+|in\s+|for\s+)([a-zA-Z\s\-]{2,40})$",
        normalized_text,
    )
    if match:
        candidate = match.group(1).strip(" .,?!")
        candidate = re.sub(
            r"\b(today|now|right\s+now|please)\b", "", candidate
        ).strip()
        if candidate and candidate not in {"the", "my", "here", "aaj", "ka"}:
            return candidate.title()

    return ""


def _build_ssl_contexts():
    contexts = [None]
    try:
        contexts.append(ssl.create_default_context())
    except Exception:
        pass
    try:
        contexts.append(ssl._create_unverified_context())
    except Exception:
        pass
    return contexts


def _http_get_json(url: str, timeout: int = 8):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"{ASSISTANT_NAME}/1.0 ({CREATOR_NAME})"},
    )
    last_exc = None
    for ctx in _build_ssl_contexts():
        try:
            if ctx is None:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    raw = resp.read().decode("utf-8", errors="replace")
                    return json.loads(raw)
            else:
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                    raw = resp.read().decode("utf-8", errors="replace")
                    return json.loads(raw)
        except Exception as exc:
            last_exc = exc
            if "CERTIFICATE_VERIFY_FAILED" not in str(exc) and ctx is not None:
                break
    if last_exc:
        raise last_exc
    return {}


def _fetch_wttr(place: str):
    is_arunachal = place.lower() in [d.lower() for d in ARUNACHAL_DISTRICTS]
    query_place = f"{place}, Arunachal Pradesh, India" if is_arunachal else place
    encoded = urllib.parse.quote(query_place)
    url = f"https://wttr.in/{encoded}?format=j1"
    data = _http_get_json(url, timeout=8)
    current = (data.get("current_condition") or [{}])[0]
    temp_c = current.get("temp_C")
    desc_list = current.get("weatherDesc") or [{}]
    desc = (desc_list[0].get("value") or "").strip()
    humidity = current.get("humidity")
    if temp_c and desc:
        return f"Weather in {place}: {desc}, {temp_c}°C (Humidity: {humidity}%)."
    return None


def _fetch_open_meteo(place: str):
    queries = [f"{place}, Arunachal Pradesh", place]
    for q in queries:
        geo_url = (
            "https://geocoding-api.open-meteo.com/v1/search?"
            f"name={urllib.parse.quote(q)}&count=1&language=en&format=json"
        )
        geo = _http_get_json(geo_url, timeout=8)
        results = geo.get("results") or []
        if results:
            item = results[0]
            lat = item.get("latitude")
            lon = item.get("longitude")
            resolved_name = item.get("name") or place
            admin1 = item.get("admin1") or ""
            if lat is not None and lon is not None:
                wx_url = (
                    "https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat}&longitude={lon}¤t=temperature_2m,relative_humidity_2m,weather_code"
                )
                wx = _http_get_json(wx_url, timeout=8)
                cur = wx.get("current") or {}
                temp = cur.get("temperature_2m")
                hum = cur.get("relative_humidity_2m")
                code = cur.get("weather_code")
                if temp is not None:
                    loc_label = f"{resolved_name}, {admin1}".strip(", ")
                    return (
                        f"Weather in {loc_label}: {temp}°C "
                        f"(Code {code}, Humidity: {hum}%)."
                    )
    return None


def get_weather_report(normalized_text: str) -> str:
    place = extract_weather_location(normalized_text)
    if not place:
        return "Please tell me which district or place weather you want to check."

    errors = []
    for fetcher in (_fetch_wttr, _fetch_open_meteo):
        try:
            report = fetcher(place)
            if report:
                return report
        except Exception as exc:
            errors.append(str(exc))

    detail = f" ({errors[-1][:60]})" if errors else ""
    return f"Weather data unavailable right now for {place}{detail}."


def get_battery_report() -> str:
    try:
        from jnius import autoclass

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        IntentFilter = autoclass("android.content.IntentFilter")
        BatteryManager = autoclass("android.os.BatteryManager")

        activity = PythonActivity.mActivity
        ifil = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        intent = activity.registerReceiver(None, ifil)
        if intent is None:
            return "Battery status unavailable."

        level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
        scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, 100)
        status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, -1)
        plugged = intent.getIntExtra(BatteryManager.EXTRA_PLUGGED, 0)

        pct = int((level * 100) / scale) if (level >= 0 and scale > 0) else -1
        is_charging = (
            status == BatteryManager.BATTERY_STATUS_CHARGING
            or status == BatteryManager.BATTERY_STATUS_FULL
            or plugged > 0
        )
        charge_txt = "Charging" if is_charging else "Not charging"
        if pct >= 0:
            return f"Battery is at {pct}% and {charge_txt}."
        return f"Battery status: {charge_txt}."
    except Exception:
        return "Battery info is available on Android device."


class AndroidVoiceBridge:
    def __init__(self, on_speech_result, on_error, on_status=None):
        self.on_speech_result = on_speech_result
        self.on_error = on_error
        self.on_status = on_status
        self.tts = None
        self.tts_ready = False
        self._pending_speech = None
        self._utt_counter = 0
        self._init_android()

    def _notify_status(self, msg: str):
        if self.on_status:
            Clock.schedule_once(lambda dt, m=msg: self.on_status(m), 0)

    def _init_android(self):
        try:
            from jnius import PythonJavaClass, autoclass, java_method

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Locale = autoclass("java.util.Locale")
            TextToSpeech = autoclass("android.speech.tts.TextToSpeech")

            self.activity = PythonActivity.mActivity
            outer_ref = self

            class TTSListener(PythonJavaClass):
                __javainterfaces__ = ["android/speech/tts/TextToSpeech$OnInitListener"]
                __javacontext__ = "app"

                @java_method("(I)V")
                def onInit(self, status):
                    def _apply():
                        if status == TextToSpeech.SUCCESS and outer_ref.tts is not None:
                            try:
                                for loc in (Locale.US, Locale.UK, Locale.getDefault()):
                                    try:
                                        res = outer_ref.tts.setLanguage(loc)
                                        if res not in (
                                            TextToSpeech.LANG_MISSING_DATA,
                                            TextToSpeech.LANG_NOT_SUPPORTED,
                                        ):
                                            break
                                    except Exception:
                                        continue
                                outer_ref.tts.setSpeechRate(1.0)
                                outer_ref.tts.setPitch(1.0)
                            except Exception:
                                pass
                            outer_ref.tts_ready = True
                            queued = outer_ref._pending_speech
                            outer_ref._pending_speech = None
                            if queued:
                                outer_ref._speak_now(queued)
                        else:
                            outer_ref.tts_ready = False
                            outer_ref._notify_status(f"TTS init failed ({status})")

                    Clock.schedule_once(lambda dt: _apply(), 0)

            self._listener = TTSListener()
            self.tts = TextToSpeech(self.activity, self._listener)
        except Exception as exc:
            self.tts = None
            self.tts_ready = False
            self._notify_status(f"TTS unavailable: {str(exc)[:60]}")

    def _speak_now(self, text: str):
        try:
            from jnius import autoclass

            TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
            Build = autoclass("android.os.Build")
            self._utt_counter += 1
            utt_id = f"silpia_{self._utt_counter}"

            if Build.VERSION.SDK_INT >= 21:
                Bundle = autoclass("android.os.Bundle")
                params = Bundle()
                params.putFloat(TextToSpeech.Engine.KEY_PARAM_VOLUME, 1.0)
                self.tts.speak(text, TextToSpeech.QUEUE_FLUSH, params, utt_id)
            else:
                HashMap = autoclass("java.util.HashMap")
                params = HashMap()
                params.put(TextToSpeech.Engine.KEY_PARAM_VOLUME, "1.0")
                self.tts.speak(text, TextToSpeech.QUEUE_FLUSH, params)
        except Exception as exc:
            self._notify_status(f"Speak error: {str(exc)[:60]}")

    def speak(self, text: str):
        if not text:
            return
        try:
            if self.tts is None:
                self._init_android()
            if self.tts is not None and not self.tts_ready:
                self._pending_speech = text
                return
            if self.tts is not None and self.tts_ready:
                self._speak_now(text)
        except Exception as exc:
            self._notify_status(f"TTS error: {str(exc)[:60]}")

    def start_listening(self):
        try:
            from android import activity as android_activity
            from jnius import autoclass

            Intent = autoclass("android.content.Intent")
            RecognizerIntent = autoclass("android.speech.RecognizerIntent")

            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM,
            )
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-IN")
            intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 5)
            intent.putExtra(
                RecognizerIntent.EXTRA_PROMPT,
                f"Speak to {ASSISTANT_NAME}...",
            )

            request_code = 7001

            def _on_result(req_code, result_code, data):
                if req_code != request_code:
                    return
                try:
                    android_activity.unbind(on_activity_result=_on_result)
                except Exception:
                    pass

                Activity = autoclass("android.app.Activity")
                if result_code == Activity.RESULT_OK and data is not None:
                    matches = data.getStringArrayListExtra(
                        RecognizerIntent.EXTRA_RESULTS
                    )
                    if matches and matches.size() > 0:
                        candidates = [str(matches.get(i)) for i in range(matches.size())]
                        chosen = self._pick_best_candidate(candidates)
                        Clock.schedule_once(
                            lambda dt, c=chosen: self.on_speech_result(c), 0
                        )
                        return

                Clock.schedule_once(
                    lambda dt: self.on_error("Could not hear clearly."), 0
                )

            android_activity.bind(on_activity_result=_on_result)
            self.activity.startActivityForResult(intent, request_code)
        except Exception as exc:
            self.on_error(f"Mic unavailable: {str(exc)[:60]}")

    def _pick_best_candidate(self, candidates):
        for cand in candidates:
            norm = normalize_command(cand)
            if any(d.lower() in norm for d in ARUNACHAL_DISTRICTS):
                return cand
        return candidates[0]


class SilpiaRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=12, spacing=8, **kwargs)
        Window.clearcolor = (0.05, 0.05, 0.07, 1)

        default_state = {
            "creator": CREATOR_NAME,
            "assistant": ASSISTANT_NAME,
            "mode": "ACTIVE",
            "history": [],
        }
        self.state = load_json(DATA_FILE, default_state)
        self.notes = load_json(NOTES_FILE, [])

        self.header_label = Label(
            text=f"{ASSISTANT_NAME} [{self.state.get('mode', 'ACTIVE')}]",
            font_size="22sp",
            size_hint_y=None,
            height=42,
            bold=True,
        )
        self.add_widget(self.header_label)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.log_label = Label(
            text="",
            font_size="15sp",
            size_hint_y=None,
            halign="left",
            valign="top",
            text_size=(Window.width - 28, None),
        )
        self.log_label.bind(texture_size=self._update_log_height)
        Window.bind(width=self._on_window_width)
        self.scroll.add_widget(self.log_label)
        self.add_widget(self.scroll)

        self.input_box = TextInput(
            hint_text="Type command or tap Voice Test",
            multiline=False,
            size_hint_y=None,
            height=44,
        )
        self.input_box.bind(on_text_validate=self._on_send_pressed)
        self.add_widget(self.input_box)

        send_btn = Button(text="Send / Test", size_hint_y=None, height=44)
        send_btn.bind(on_press=self._on_send_pressed)
        self.add_widget(send_btn)

        hello_btn = Button(text="Test Voice (Hello Sir)", size_hint_y=None, height=44)
        hello_btn.bind(on_press=self._on_hello_pressed)
        self.add_widget(hello_btn)

        mic_btn = Button(text="Voice Test (Mic)", size_hint_y=None, height=46)
        mic_btn.bind(on_press=self._on_mic_pressed)
        self.add_widget(mic_btn)

        self.voice = AndroidVoiceBridge(
            on_speech_result=self._on_voice_heard,
            on_error=self._on_voice_error,
            on_status=self._on_voice_status,
        )

        self._refresh_log_view()
        self._request_android_permissions()

    def _request_android_permissions(self):
        try:
            from android.permissions import Permission, request_permissions

            request_permissions(
                [Permission.RECORD_AUDIO, Permission.INTERNET],
                lambda perms, grants: None,
            )
        except Exception:
            pass

    def _on_window_width(self, instance, width):
        self.log_label.text_size = (max(100, width - 28), None)

    def _update_log_height(self, instance, value):
        self.log_label.height = value[1] + 20
        self.scroll.scroll_y = 0

    def _append_line(self, line: str):
        now_str = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{now_str}] {line}"
        hist = self.state.setdefault("history", [])
        hist.append(formatted)
        if len(hist) > 120:
            self.state["history"] = hist[-120:]
        save_json(DATA_FILE, self.state)
        self._refresh_log_view()

    def _refresh_log_view(self):
        self.header_label.text = (
            f"{ASSISTANT_NAME} [{self.state.get('mode', 'ACTIVE')}]"
        )
        lines = self.state.get("history", [])[-25:]
        self.log_label.text = "\n".join(lines)
        Clock.schedule_once(lambda dt: setattr(self.scroll, "scroll_y", 0), 0.05)

    def _on_voice_status(self, status_msg: str):
        self._append_line(f"{ASSISTANT_NAME} [TTS]: {status_msg}")

    def _on_hello_pressed(self, instance):
        msg = f"Hello Sir, {ASSISTANT_NAME} created by {CREATOR_NAME} is ready."
        self._append_line(f"{ASSISTANT_NAME}: {msg}")
        self.voice.speak(msg)

    def _on_mic_pressed(self, instance):
        self.voice.start_listening()

    def _on_voice_heard(self, spoken_text: str):
        self._append_line(f"Voice: {spoken_text}")
        self._process_command(spoken_text)

    def _on_voice_error(self, err_msg: str):
        self._append_line(f"{ASSISTANT_NAME}: {err_msg}")

    def _on_send_pressed(self, instance):
        raw = (self.input_box.text or "").strip()
        if not raw:
            return
        self.input_box.text = ""
        self._append_line(f"You: {raw}")
        self._process_command(raw)

    def _process_command(self, raw_text: str):
        norm = normalize_command(raw_text)
        if not norm:
            return

        if any(w in norm for w in ["sleep", "so ja", "rest"]):
            self.state["mode"] = "SLEEPING"
            save_json(DATA_FILE, self.state)
            reply = f"{ASSISTANT_NAME} is now sleeping."
            self._respond(reply)
            return

        if any(w in norm for w in ["wake up", "utho", "active"]):
            self.state["mode"] = "ACTIVE"
            save_json(DATA_FILE, self.state)
            reply = f"Yes Sir, {ASSISTANT_NAME} is active."
            self._respond(reply)
            return

        if any(w in norm for w in ["hello", "hi", "namaste", "hey"]):
            reply = f"Hello Sir, how can {ASSISTANT_NAME} help you?"
            self._respond(reply)
            return

        if any(
            w in norm
            for w in [
                "creator",
                "developer",
                "owner",
                "who made you",
                "who create you",
                "who created you",
                "malik",
            ]
        ):
            reply = f"I am {ASSISTANT_NAME}, created by {CREATOR_NAME}."
            self._respond(reply)
            return

        if "help" in norm or any(w in norm for w in ["feature", "features", "module", "modules"]):
            reply = (
                "Available commands: Time, Date, Month, Year, Weather, "
                "Battery, Note, Last note, Sleep, Wake up, and Creator."
            )
            self._respond(reply)
            return

        if "battery" in norm:
            self._respond(get_battery_report())
            return

        has_month = "month" in norm or "mahina" in norm
        has_year = "year" in norm or "saal" in norm
        if has_month and has_year:
            now_m = datetime.now().strftime("%B")
            now_y = datetime.now().strftime("%Y")
            self._respond(f"Current month is {now_m} and year is {now_y}.")
            return

        if "time" in norm or "samay" in norm:
            now_t = datetime.now().strftime("%I:%M %p")
            self._respond(f"Current time is {now_t}.")
            return

        if "date" in norm or "tarikh" in norm or "aaj" in norm:
            now_d = datetime.now().strftime("%d %B %Y")
            self._respond(f"Today's date is {now_d}.")
            return

        if has_month:
            now_m = datetime.now().strftime("%B")
            self._respond(f"Current month is {now_m}.")
            return

        if has_year:
            now_y = datetime.now().strftime("%Y")
            self._respond(f"Current year is {now_y}.")
            return

        if "last note" in norm:
            if not self.notes:
                self._respond("No notes saved yet.")
            else:
                self._respond(f"Last note: {self.notes[-1]['note']}")
            return

        if norm.startswith("note ") or norm.startswith("create note "):
            note_text = re.sub(
                r"^(?:create\s+)?note\s+", "", raw_text, flags=re.IGNORECASE
            ).strip()
            if note_text:
                self.notes.append(
                    {"time": datetime.now().isoformat(), "note": note_text}
                )
                save_json(NOTES_FILE, self.notes)
                self._respond(f"Note saved: {note_text}")
            else:
                self._respond("Please tell me what note to save.")
            return

        if "notes" in norm:
            if not self.notes:
                self._respond("No notes saved yet.")
            else:
                latest = self.notes[-1]["note"]
                self._respond(f"You have {len(self.notes)} notes. Latest: {latest}")
            return

        has_place = bool(extract_weather_location(norm))
        if "weather" in norm or "mosam" in norm or "mausam" in norm or has_place:
            self._append_line(f"{ASSISTANT_NAME}: Checking weather...")
            threading.Thread(
                target=self._weather_worker, args=(norm,), daemon=True
            ).start()
            return

        self._respond(f"Heard: {raw_text}")

    def _weather_worker(self, norm_cmd: str):
        report = get_weather_report(norm_cmd)
        Clock.schedule_once(lambda dt, r=report: self._respond(r), 0)

    def _respond(self, message: str):
        self._append_line(f"{ASSISTANT_NAME}: {message}")
        self.voice.speak(message)


class SilpiaApp(App):
    def build(self):
        self.title = ASSISTANT_NAME
        return SilpiaRoot()


if __name__ == "__main__":
    SilpiaApp().run()