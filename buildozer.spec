[app]
title = Tap to Breathe
package.name = taptobreathe
package.domain = org.yourname
source.dir = .
source.include_exts = py,txt
version = 1.0.0
requirements = python3,pygame
orientation = portrait
fullscreen = 1

# Keep portrait gameplay stable on most phones.
android.api = 34
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True

# Optional: include this if you want a custom app icon later.
# icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
