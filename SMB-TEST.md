# SMB library test: add-on 0.7.22 + Helper 0.2.9

**Helper source only. A signed 0.2.9 APK must be built before testing. Helper 0.2.8 does not support SMB bridge sessions.**

## Build

1. Extract the build-package ZIP and open its android-helper folder in Android Studio.
2. Let Gradle sync finish, then build a signed release APK using the existing Helper keystore and alias.
3. Version is already 0.2.9 / versionCode 12.
4. If updating your previous working Android Studio project, copy BOTH Java files:
   app/src/main/java/com/stormtracker/zidoobridge/DiagnosticActivity.java
   app/src/main/java/com/stormtracker/zidoobridge/MediaPath.java
   Also retain the AndroidManifest.xml storage-permission change and set versionCode 12 / versionName 0.2.9. Keep your working Gradle/plugin versions.
5. Do not share your keystore or passwords.

## Install and test

1. Update the Zidoo with your signed Helper 0.2.9 APK.
2. Open the Helper, allow storage permission on Android 6–9, and save a diagnostic report.
3. Install the included Kodi-for-Zidoo-0.7.22-test.zip inside Kodi and fully restart Kodi.
4. Open Kodi for Zidoo add-on settings and enable **Test SMB library playback**.
5. Use a complete credential-free smb://host/share/folder/movie.mkv path in Kodi's scanned video library.
   Store Kodi credentials separately; embedded login/password URLs are not supported.
6. First confirm Zidoo File Explorer plays the same NAS file using its saved connection.
7. Select the file inside Movies, TV shows or Music videos. The native Zidoo player should launch.
8. Exit normally and check Kodi's final resume bookmark.
9. Play again and check native Zidoo resume.
10. Exit below 90% and confirm the resume point; exit at 90% or above and check automatic watched marking.
11. Repeat with another file, a TV episode, and a local /storage/ file.
12. Save the Helper report and Kodi log if a step fails. Review before sharing.

## Scope

SMB library routing is opt-in and uses Zidoo's saved NAS credentials. No password-file import, new credential storage, mount creation or path redirection settings are included.
The mapping is based on the tester's successful Z9X 8K report:
smb://host/share/folder/file → /mnt/smb/host#share/folder/file.
Both components compare the complete host/share/folder/filename identity. Spaces and UTF-8 escapes are decoded; case is preserved.
Credentials, explicit ports, IPv6 hosts, malformed paths, encoded path separators, dot traversal, queries and fragments are rejected.
Other firmware may use a different return-path convention; mismatches must leave the library unchanged.

Local playback, the 90% watched threshold, legacy Android export and guarded session reset are retained.
Home widgets/shortcuts, Videos → Files and arbitrary add-on streams remain outside this test. Kodi's restart issue remains.
The Helper's separate SMB diagnostic button still performs a standalone test without a Kodi library update.

31 automated add-on tests passed, including original-library update and idempotent retry for a mounted SMB result.
Python and Java syntax checks passed. The Helper has not been compiled in this environment, and integrated SMB playback/resume/watched behavior still needs device testing.
The tester report established standalone SMB launch and native results on Z9X 8K; it does not establish integrated Kodi support yet.
