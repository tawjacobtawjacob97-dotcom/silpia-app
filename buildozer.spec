[app]

# (str) Title of your application
title = Silpia

# (str) Package name
package.name = silpia

# (str) Package domain (needed for android packaging)
package.domain = org.silpia

# (source) Where the source files are located
source.dir = .

# (list) Source files to include (let empty to include all files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (list) List of exclusions to pack into the apk
#source.exclude_exts = spec

# (str) Application versioning (method 1)
version = 0.1[cite: 7]

# (list) Application requirements
requirements = python3.10,kivy[cite: 7]

# (str) Supported orientations
orientation = portrait[cite: 1, 7]

# 
# Android specific
#
android.python_version = 3.10

# (list) Permissions
android.permissions = INTERNET, RECORD_AUDIO[cite: 7]

# (int) Target Android API, should be as high as possible.
android.api = 31[cite: 7]

# (int) Minimum API your APK will support.
android.minAPI = 21[cite: 7]

# (bool) Use D8 for dexing
android.use_dex = True[cite: 7]

# (bool) Automatically accept Android SDK license
android.accept_sdk_license = True[cite: 7]
