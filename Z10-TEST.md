# Z10 / Android 7 compatibility test — source only

This branch contains Helper 0.2.8 source and matching add-on 0.7.21 source.
There is **no compiled or signed Helper 0.2.8 APK yet**. Do not install Helper
0.2.7 and expect these source changes to take effect.

## What changed

On Android 6–9, the Helper requests storage permission and writes reports,
ready messages and native playback results to the shared
Download/ZidooBridge folder. Files are written to a temporary file and renamed
after the write completes. Android 10+ retains its MediaStore export path.

The add-on accepts Helper 0.2.8 results and uses the 90% watched threshold.
Shortcut diagnostics are retained; SMB and shortcut routing are not fixed.
The older Zidoo player intent, result extras and localhost status API remain
unverified on Z10 firmware 2.3.88.

## Build on Windows

1. Download this branch using Code > Download ZIP and extract it.
2. Open its android-helper folder as a project in Android Studio.
3. Build a signed release APK using the same keystore and alias used for
   Helper 0.2.7. Do not share the keystore or password.
4. This project sets versionCode 11 / versionName 0.2.8. If Gradle/plugin
   versions differ from your working setup, use your existing working project
   and replace these three files with the versions in this branch:
   - app/src/main/java/com/stormtracker/zidoobridge/DiagnosticActivity.java
   - app/src/main/AndroidManifest.xml
   - app/build.gradle (retain your working plugin configuration).
5. Copy addon_0.7.21 to a folder named
   plugin.program.zidoo.bridge.diagnostic and zip that folder with all its
   contents. That ZIP is the Kodi add-on installer.

A successful Android build is required before sending the APK to the tester.
No Android SDK, Java compiler or release signing key is available in the
preparation environment, so this Helper source has not been compiled here.
The matching add-on passed 23 automated tests:
python -m unittest discover -s tests_0.7.21

## Device test

1. Update the Helper with the signed 0.2.8 APK.
2. Open it directly and allow the Android storage permission prompt.
3. Use a complete local /storage/... movie filename, test native playback,
   then save a diagnostic report. Confirm the report exists under
   Internal storage/Download/ZidooBridge.
4. Install the matching 0.7.21 add-on ZIP in Kodi and fully restart Kodi.
5. Select a local movie inside the Movies library.
6. Verify launch, native resume, final bookmark, watched marking at 90% and
   return to Kodi. Save the Helper report and Kodi log if a step fails.

Kodi may also need storage permission to read the shared report. SMB paths,
including smb://127.0.0.1 mappings, remain unsupported.
Successful export removes the reported preflight blocker; it does not establish
full Z10 compatibility until playback and result-return tests pass.

Do not publish passwords, signing keys or unreviewed logs. The main branch's
signed APK remains 0.2.7; this is a separate development test.

## Additional tester features in Helper 0.2.8

### Experimental SMB test — diagnostics only

Open the Helper directly. Enter a complete movie URL such as:

`smb://192.168.1.194/MEDIAS/FILMS/MKV UHD REMUX/Avatar Fire and Ash (2025)/actual-movie-filename.mkv`

The filename above is a placeholder: replace it with the real filename.
Capitalization is preserved; spaces are encoded for the URI. Do not enter a
username or password in the URL. URLs with credentials, queries or fragments
are rejected. Special filename characters such as # must be URI-encoded.

First confirm the file plays in Zidoo File Explorer with its saved NAS login.
Press **Test experimental SMB path (no Kodi update)**, not the local test button.
This passes an SMB URI directly to the native player. Whether older or newer
firmware accepts it and reuses saved credentials is not yet known.
Save the diagnostic report whether playback succeeds or fails.

This does not add NAS support to Kodi playback or change resume/watched state.
A share root or movie folder is not a playable file. No password-file import,
mount mapping or credential storage is implemented.

### Reset pending session

Open the Helper directly, which now displays diagnostics even with a saved
pending session. Close native playback. If diagnostic polling is running,
press Stop diagnostic polling and wait for the worker to finish.
Press **Reset pending session (player must be closed)**.

The Helper checks the localhost player API and permits reset only for a
successful response reporting status 806 (no active playback). Network errors,
unknown statuses and active diagnostic workers block reset.
For a bridge session, it exports a cancelled/error result before clearing
Helper state. The matching add-on rejects that result and clears its pending
session without updating resume or watched state; a result-rejected notification
may appear. If export fails, reset does not clear the pending session.

### Diagnostics and validation

Reports now include Android/API version, model/manufacturer, firmware build,
launch mode and standalone player result code/position/duration.
Launch accepted still does not mean playback succeeded.

23 add-on tests pass, including cancelled-session handling without library
writes. Helper Java syntax was parsed successfully. This is not an Android
compile or device test; a signed Android Studio build and real device tests
remain required.
