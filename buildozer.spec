[app]

title = Silpia
package.name = silpia
package.domain = org.silpia
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy,speechrecognition

orientation = portrait

# 
# Android specific
#
android.python_version = 3.10

p4a.branch = master

android.permissions = INTERNET, RECORD_AUDIO

android.api = 31

android.minAPI = 21

android.use_dex = True

android.accept_sdk_license = True
