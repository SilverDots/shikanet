# Shikanet - A message summarization app

A convenient mobile app using LLMs to summarize sample conversation history.

Requirements:
- Flutter SDK
- Android emulator

To run this app:
1) Execute the backend server by running `python flask_app/app.py`
2) Open the android emulator and launch a new emulator instance (can be done via VSCode)
3) If you are using VSCode, you can run the app by navigating to `/mobile/lib/main.dart` and running the app in the IDE.
   If you are not using VSCode, first run `flutter devices` to get the device ID of your android emulator. Then,
   run `flutter run -d [emulator_id]`
