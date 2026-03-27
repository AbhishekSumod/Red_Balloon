# Tap to Breathe - Android Build Guide

This project is set up to build for Android using Buildozer.

## 1) Prerequisites (recommended in WSL Ubuntu or Linux)

- Python 3.10+ installed
- Java JDK 17 installed
- Git installed
- Build tools:

```bash
sudo apt update
sudo apt install -y \
  git zip unzip openjdk-17-jdk \
  python3-pip python3-venv \
  autoconf libtool pkg-config \
  zlib1g-dev libncurses5-dev libncursesw5-dev \
  libtinfo5 cmake libffi-dev libssl-dev
```

## 2) Install Buildozer

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install buildozer cython
```

## 3) Build debug APK

From the project folder:

```bash
buildozer android debug
```

First build takes longer because Android SDK/NDK are downloaded.

Output APK path is usually:

```text
bin/taptobreathe-1.0.0-arm64-v8a-debug.apk
```

## 4) Install on connected Android phone

Enable Developer Options + USB Debugging on phone, then:

```bash
buildozer android deploy run logcat
```

## 5) Build release (for store upload)

```bash
buildozer android release
```

Then sign the artifact (APK/AAB) with your keystore before Play Store upload.

## Notes

- Entry point is `main.py` (already added), which starts `tap_to_breathe.py`.
- Game controls are touch-ready: tap to boost, drag to move.
- If build fails due to local toolchain mismatch, keep `buildozer.spec` as-is and update Buildozer/p4a in your virtual environment.
