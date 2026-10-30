[app]

# (str) Title of your application
title = Silpia

# (str) Package name
package.name = silpia

# (str) Package domain (needed for android packaging)
package.domain = org.silpia

# (str) Source directory where your app files are located
source.dir = .

# (list) Source files to include (let it include python files and assets)
source.include_exts = py,png,jpg,kv,atlas,mp3,txt

# (list) Source files to exclude (optional)
source.exclude_exts = spec

# (list) List of inclusion/exclusion patterns
source.include_patterns = assets/*,images/*.png

# (str) Application versioning
version = 1.0

# (list) Application requirements
# Note: pyttsx3 aur playsound ki jagah android par gtts aur android sound APIs behtar kaam karte hain,
# lekin filhal hum aapki zaroorat ke hisaab se core libraries daal rahe hain.
requirements = python3,kivy,speechrecognition,pyautogui,opencv-python,gtts,playsound

# (str) Supported orientations
orientation = portrait

# (list) Permissions
# Yeh permissions mic, storage aur internet ke liye zaroori hain
android.permissions = INTERNET,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android SDK version to use
android.sdk = 31

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Enable Android auto backup
android.accept_sdk_license = True
