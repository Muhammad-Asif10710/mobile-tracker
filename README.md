# Mobile Inventory Tracker

A lightweight mobile inventory application built with Python and Kivy for Android devices.

## Files Included

- `main.py` - Kivy application with SQLite storage, internal file handling, image copying, and search functionality.
- `buildozer.spec` - Buildozer configuration for Android with `arm64-v8a` support and required permissions.

## Usage Guide

### 1. Install Buildozer

On a Linux development machine:

```bash
sudo apt update
sudo apt install -y buildozer python3-pip
pip3 install --user cython kivy
```

> If you are using a container or virtual environment, make sure `buildozer` is installed in the same environment.

### 2. Initialize and Build

From the project root:

```bash
cd /workspaces/mobile-tracker
buildozer android debug
```

This command compiles the app for Android using the settings in `buildozer.spec`.

### 3. Install on Device

Connect your Pixel 6a or other Android device with USB debugging enabled, then run:

```bash
buildozer android deploy run
```

### 4. App Workflow

1. Launch the app on your Android device.
2. Enter the object name into the text field.
3. Tap `Choose Image` and select a photo from device storage.
4. Tap `Save Object` to store the item and copy its image into the internal app directory.
5. Use the `Search` field and button to query items by exact name (case-insensitive).
6. The app displays the stored image and updates the bottom status bar with success or error messages.

### 5. Storage Behavior

- Database is stored in the app sandbox using `App.get_running_app().user_data_dir`.
- Images are copied as raw binary bytes into `stored_images/` inside the app container.
- SQLite is used for reliable local storage and avoids file locking issues.

## Notes

- The app targets Android architecture `arm64-v8a`.
- Permissions for `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE`, and `MANAGE_EXTERNAL_STORAGE` are requested in `buildozer.spec`.
