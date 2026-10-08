# Kodi for Zidoo

Preview release for native Zidoo playback from Kodi video libraries.

Install the signed Helper APK and add-on ZIP using **Kodi for Zidoo install.txt**.
Kodi itself is not bundled. Movies, TV episodes and music videos use the native
player, with native resume and automatic watched marking at 95% final position.

Tested on Z30 Pro / firmware v1.3.45 / Android 11 / Kodi 22 BETA2 ARM 32-bit.
Other hardware and Kodi versions are unverified.

Known issue: Kodi 22 can restart during native playback, showing Home before
restoring the saved library list. See [Kodi issue #29691](https://github.com/xbmc/xbmc/issues/29691).

0.7.19 removes the experimental Python external-player route and its settings;
legacy bridge-owned test rules are removed. Helper 0.2.7 is the existing signed
APK supplied by the tester, with no APK rebuild in this release preparation.
The new add-on packaging has automated checks but still needs device smoke testing.

Source contains the add-on, full Helper Android Studio project, and tests.
Build Helper with your own signing key for a fork; never commit signing keys,
passwords, local.properties, diagnostic reports or user Kodi profiles.
