[app]

# (str) Title of your application
title = Silpia

# (str) Package name
package.name = silpia

# (str) Package domain (needed for android packaging)
package.domain = org.silpia

# (list) Source files to include (let it include all files in the directory)
source.dir = .

# (list) Source file extensions to include (let it include py, png, jpg, kv, atlas)
source.exts = py,png,jpg,kv,atlas

# (str) Application versioning (determined by version)
version = 0.1

# (list) Application requirements
# यहाँ gtts, kivy और pyjnius को जोड़ दिया गया है
requirements = python3,kivy,pyjnius,gtts

# (str) Custom source folders for requirements
#requirements.source.kivy = ../../kivy

# (list) PERMISSIONS
android.permissions = INTERNET, RECORD_AUDIO

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minAPI = 21

# (bool) Use D8 for dexing
android.use_dex = True

# (bool) Automatically accept Android SDK license
android.accept_sdk_license = True

# (str) python-for-android branch (Python 3.14 की एरर रोकने के लिए स्थिर ब्रांच)
p4a.branch = release-2024.01.3

orientation = portrait

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_root = 1