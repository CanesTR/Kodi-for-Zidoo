# Kodi for Zidoo 0.7.21 + Helper 0.2.8 — tester package

[Download the complete test package](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/testing/0.7.21/Kodi-for-Zidoo-0.7.21-Helper-0.2.8-test-package.zip)

Or download components separately:
- [Signed Helper 0.2.8 APK](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/testing/0.7.21/Kodi-for-Zidoo-Helper-0.2.8.apk)
- [Add-on 0.7.21 test ZIP](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/testing/0.7.21/Kodi-for-Zidoo-0.7.21-test.zip)
- [Checksums](SHA256SUMS.txt)
- [Source and build notes](https://github.com/CanesTR/Kodi-for-Zidoo/tree/android-7-compatibility-test)

## Install

1. Extract the outer test package. It contains the APK and a separate add-on ZIP.
2. Install Helper 0.2.8 on the Zidoo as an update. Its signing certificate matches the previous Helper 0.2.7.
3. Open the Helper directly. On Android 6–9, allow the storage permission prompt.
4. Test a complete local movie filename beginning with `/storage/`, then save a diagnostic report. Confirm it is in Internal storage/Download/ZidooBridge.
5. In Kodi, install **Kodi-for-Zidoo-0.7.21-test.zip** using Add-ons → Install from zip file. Do not install the outer package.
6. Fully close and reopen Kodi.
7. Select a scanned local movie, episode or music video inside the Kodi video library.

Keep Kodi and the Helper's shared Downloads access enabled. No Android Studio is needed to install this tester package.

## Local playback and Android 7 test

Verify Zidoo launches, native resume appears when appropriate, and exiting returns the final bookmark to Kodi.
At a final playback position below 90%, check the resume bookmark. At 90% or above, check automatic watched marking.
Seeking counts toward the threshold. Kodi may still restart during native playback.
On Z10 Android 7.1.1 / firmware 2.3.88, report export and native player/API compatibility need real-device verification.

## Experimental SMB test — Helper only

First confirm the same file plays in Zidoo File Explorer without requesting credentials.
Enter a **complete** `smb://host/share/folder/movie.mkv` URL in the Helper path field.
Press **Test experimental SMB path (no Kodi update)**.
Capitalization is preserved and spaces are encoded. Do not include a login or password.
Share roots and movie folders alone are not accepted. Encode special filename characters such as # as %23.
Exit normally and save the diagnostic report, whether playback succeeds or fails.

This is a direct SMB URI experiment using Zidoo's saved NAS connection. It does **not** enable NAS playback from Kodi, update Kodi watched/resume state for SMB, import password files or mount shares.
Whether the native player accepts the URI and saved credentials remains unverified.

## Pending-session reset

Close native playback. Open the Helper directly.
If polling is running, press Stop diagnostic polling and wait for it to finish.
Press **Reset pending session (player must be closed)**.

Reset proceeds only when the localhost player API successfully reports status 806 (no active playback).
Unknown status, connection errors or a running diagnostic worker block reset.
For a bridge session, the Helper exports a cancelled result before clearing its state.
The matching add-on rejects the cancelled result and clears its pending session without changing the library.
A result-rejected notification may appear. If export fails, the Helper retains the pending session.

## Home shortcut/widget diagnostics

Routing behavior is unchanged. Test a local library movie through the failing shortcut with Kodi debug logging enabled and save the Kodi log.
Videos → Files and home shortcuts/widgets remain unverified; select items inside Movies/TV shows/Music videos for the normal test.

## Report results

Include model, firmware, Android version, exact Kodi version/build, skin and both component versions.
State whether you used the library, Files, a home widget, the local Helper test or the SMB Helper test.
Include exact messages and results for playback, resume, watched state and return.
Save a Helper diagnostic report before clearing app data. Review logs before sharing; do not post passwords or credential XML files.

APK manifest confirms version 0.2.8 / versionCode 11 / min SDK 23 / target SDK 28.
Its v1 signature and signed entry digests were checked, and its signing certificate matches Helper 0.2.7.
The matching add-on passed 23 automated tests. Device functionality has not yet been verified for this package.
The regular public preview remains 0.7.19 + Helper 0.2.7.
