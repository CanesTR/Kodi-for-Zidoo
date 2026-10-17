# Zidoo System Inspector 0.1.0

Separate, read-only Android 10+ diagnostic app. It does not replace Kodi or the Helper.

The diagnostic Kodi reports repeatedly recorded reason 10 and `stop ... due to from pid 2290` during native playback. Home-only and File Explorer controls resumed with the same Kodi PID. Some later stops came from PID 12575; neither caller has been identified. These are observations, not proof of a specific firmware component or allowlist.

Android 11 ActivityManagerService constructs the `from pid` description in `forceStopPackage`. The next step is to inspect installed system apps that have FORCE_STOP_PACKAGES granted, and the Zidoo player/launcher. Static APK inspection may reveal exclusion lists or playback cleanup code, but cannot by itself prove that a package owned a historical PID.

Install the Actions artifact APK, open **Zidoo System Inspector**, select **Save analysis ZIP to Downloads**, and wait for the saved message. Send the ZIP from **Internal storage/Download/ZidooSystemInspector** privately for analysis. It contains selected system APK copies, package names, UIDs, versions, requested permissions, firmware fingerprint, and any process names Android exposes. It excludes app data, user settings, media URLs and credentials. Unreadable APKs are noted in the report. Export can require substantial free space.

No network permission, storage permission prompt, ADB, root, developer options, settings writes, playback launch, or force-stop capability. QUERY_ALL_PACKAGES is used only for the installed-system-package inspection. Process visibility is restricted on Android; missing PID names are expected and inconclusive.

References:
- https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-11.0.0_r1/services/core/java/com/android/server/am/ActivityManagerService.java
- https://github.com/bowlingbeeg/PlexToZidoo/blob/main_bowlingbeeg/README.md (developer describes background process limits; not proof of our device's force-stop source)

The workflow builds a debug-signed test APK and verifies its signature. It does not rebuild diagnostic Kodi or modify the working bridge. Source license: GPL-2.0-or-later, following this project's diagnostic code; see ../kodi-exit-v1/COPYING.
