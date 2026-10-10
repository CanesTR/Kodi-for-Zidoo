# Kodi for Zidoo

Preview release for native Zidoo playback from Kodi video libraries.

Install the signed Helper APK and add-on ZIP using **Kodi for Zidoo install.txt**.
Kodi itself is not bundled. Movies, TV episodes and music videos use the native
player, with native resume and automatic watched marking at 95% final position.

Tested on Z30 Pro / firmware v1.3.45 / Android 11 / Kodi 22 BETA2 ARM 32-bit.
A tester also reports successful local-library playback, resume, and watched marking on Z9X 8K / firmware 1.3.45 / Kodi 22 beta2 ARM 32-bit with Arctic Horizon 2. Home shortcuts did not route to Zidoo in that test. Other configurations are unverified.

**Media paths must begin with `/storage/`. SMB/NAS URLs are not supported in the current preview.**

Known issue: Kodi 22 can restart during native playback, showing Home before
restoring the saved library list. See [Kodi issue #29691](https://github.com/xbmc/xbmc/issues/29691).

0.7.19 removes the experimental Python external-player route and its settings;
legacy bridge-owned test rules are removed. Helper 0.2.7 is the existing signed
APK supplied by the tester, with no APK rebuild in this release preparation.
The new add-on packaging has automated checks but still needs device smoke testing.

Source contains the add-on, full Helper Android Studio project, and tests.
Build Helper with your own signing key for a fork; never commit signing keys,
passwords, local.properties, diagnostic reports or user Kodi profiles.

## Downloads and installation

Download both components:

- [Kodi for Zidoo add-on 0.7.19](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/Kodi-for-Zidoo-0.7.19.zip)
- [Zidoo Bridge Helper 0.2.7 signed APK](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/Kodi-for-Zidoo-Helper-0.2.7.apk)
- [Installation instructions](downloads/Kodi%20for%20Zidoo%20install.txt)
- [Source archive](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/Kodi-for-Zidoo-0.7.19-source.zip)
- [SHA-256 checksums](downloads/SHA256SUMS.txt)

Install the Helper APK on the Zidoo, then install the add-on ZIP inside Kodi and fully restart Kodi. Follow the installation instructions for the complete steps. Users do not need Android Studio.

## Development

The add-on source is in `addon_0.7.19/`; the Android Studio project is in `android-helper/`.
Run the automated checks from the repository root:

```sh
python -m unittest discover -s tests_0.7.19
```

This is an independent project, not an official Kodi or Zidoo release.

## Optional test build

[0.7.20 test instructions and download](downloads/testing/README.md): changes automatic watched marking to 90% and adds shortcut selection diagnostics. Uses the existing Helper 0.2.7; device testing is pending. The default preview downloads above remain 0.7.19.
