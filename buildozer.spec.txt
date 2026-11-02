[app]

# (str) Title of your application
title = Silpia

# (str) Package name
package.name = silpia

# (str) Package domain (needed for android packaging)
package.domain = org.silpia

# (list) Source files to include (let it include python files and assets)
source.include_exts = py,png,jpg,kv,atlas,mp3

# (list) Application requirements
# यहाँ हमने सिर्फ वही वॉयस और बेसिक लाइब्रेरीज रखी हैं जो एंड्रॉइड पर आसानी से काम करती हैं और एरर नहीं देतीं
requirements = python3,kivy,speechrecognition,gtts,playsound,urllib3,certifi,idna,charset-normalizer,requests

# (str) Supported orientations
orientation = portrait

# (list) Permissions
# वॉयस असिस्टेंट के लिए माइक्रोफोन और इंटरनेट की परमिशन जरूरी है
android.permissions = INTERNET, RECORD_AUDIO, ACCESS_NETWORK_STATE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Supported architectures
android.archs = arm64-v8a, armeabi-v7a