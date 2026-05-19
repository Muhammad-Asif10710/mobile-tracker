[app]
# (str) Title of your application
title = Mobile Inventory Tracker

# (str) Package name
package.name = mobileinventorytracker

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py file is located
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,txt

# (str) Application versioning
version = 1.0
version.code = 1

# (list) Application requirements
requirements = python3,kivy,sqlite3

# (str) Supported orientation
orientation = portrait

# (list) Android architectures to build for (Fixed typo here: added 's')
android.archs = arm64-v8a

# (list) Permissions
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# (int) Android API to use
android.api = 33
android.minapi = 21
# (str) Android NDK version to use
android.ndk = 25b

# (str) Android SDK build-tools version to use
android.build_tools_version = 33.0.0

# (bool) Automatically accept SDK licenses
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
