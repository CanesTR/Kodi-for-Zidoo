# Hostname-to-IP SMB test: add-on 0.7.23 + Helper 0.2.10

Helper 0.2.10 is source only until a signed APK is built. Install both new components for this test.

## Build the Helper APK

1. Extract the build-package ZIP into a new folder.
2. In Android Studio, Open its android-helper folder and let Gradle sync finish.
3. Generate a signed release APK using the same existing Helper keystore and alias.
4. Version is already 0.2.10 / versionCode 13.
5. If using a previous working project, replace BOTH DiagnosticActivity.java and MediaPath.java under app/src/main/java/com/stormtracker/zidoobridge/.
   Retain the AndroidManifest.xml legacy storage permission and set versionCode 13 / versionName 0.2.10. Keep your working Gradle/plugin versions.
6. Do not share signing keys or passwords.

## Install and configure

1. Update the Helper with the signed 0.2.10 APK.
2. Install Kodi-for-Zidoo-0.7.23-test.zip inside Kodi, then fully close and reopen Kodi.
3. In Kodi for Zidoo > Configure, enable Test SMB library playback.
4. If Kodi uses a NAS hostname but Zidoo returns an IPv4 mount address, enter both:
   NAS hostname to map: the hostname used in Kodi's SMB source (host only).
   That NAS IPv4 address: the current address of that same NAS.
   Confirm the address in your NAS/router settings or a diagnostic report before using the mapping.
5. Leave both fields empty when hostname mapping is unnecessary.
6. You do not need to change or rescan existing library paths.
7. Confirm Zidoo File Explorer has a saved login for the NAS and plays the same video.

This is one explicit user-configured hostname/IP mapping, not automatic DNS discovery. It applies only to the configured hostname (case-insensitive hostname comparison).
The share, folders and filename remain case-sensitive and must match exactly.
If the NAS IP changes, update the setting before launching another test.

## Behavior and tests

At launch, the add-on pins the expected mount path in the pending session and passes it to the Helper.
The Helper validates that the pinned mapping changes only the host portion to an IPv4 address; it persists the identity for recovery and exports it with the result.
The add-on requires that identity to match its launch checkpoint before applying resume/watched changes.
No hostname lookup is performed during result processing. A different host/IP, share, folder or filename must not update the library.

Test a hostname-based library movie, native resume, exiting below 90%, and watched marking at 90% or above.
Repeat with a NAS file using a direct IP URL and with a local /storage/ file.
Save Helper and Kodi logs if rejected. Review before sharing; never upload credentials.
Use Kodi's Movies/TV shows/Music videos library, not Files or widgets.

SMB URLs must remain credential-free. Zidoo's saved NAS login is used.
The 90% threshold, guarded session reset and Android 6–9 export support are retained.
Kodi's restart/Home-screen issue remains.

34 automated add-on tests passed. Python syntax checks passed.
Helper compilation and real-device playback/results validation are required.
