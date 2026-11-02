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
# Specify python and kivy/other libraries your app needs
requirements = python3,kivy

# (str) Supported orientations
orientation = portrait

#
# Android specific
#

# (list) Permissions
android.permissions = INTERNET, RECORD_AUDIO

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minAPI = 21

# (bool) Use D8 for dexing
android.use_dex = True
