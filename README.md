# Android 7 compatibility development branch

**Source only: Helper 0.2.8 has not been compiled or signed.** See [Z10 build and test instructions](Z10-TEST.md). The signed APK linked below remains 0.2.7 and does not include the Android 7 fix.

# Kodi for Zidoo

Play Kodi library movies, TV episodes and music videos with Zidoo's native player, with native resume and automatic watched marking. This is an independent public preview, not an official Kodi or Zidoo release.

## Read this before installing

**Current builds require a complete local media path beginning with `/storage/` and a Kodi video library item.**

- **SMB/NAS paths are not supported yet.** This includes `smb://127.0.0.1/...` mappings of HDDs attached to the Zidoo.
- Start playback inside **Movies, TV shows or Music videos**. Videos → Files, home shortcuts and widgets are not reliably routed to Zidoo.
- The destination is **Zidoo's native player**, not ZDMC.
- Kodi itself is not bundled. Two components are required; users do not need Android Studio.

## Current downloads

| Component | Version | Purpose |
| --- | --- | --- |
| [Public preview add-on ZIP](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/Kodi-for-Zidoo-0.7.19.zip) | 0.7.19 | Automatic watched marking at 95% |
| [Signed Zidoo Bridge Helper APK](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/Kodi-for-Zidoo-Helper-0.2.7.apk) | 0.2.7 | Required with either add-on version |
| [Optional test add-on ZIP](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/testing/Kodi-for-Zidoo-0.7.20-test.zip) | 0.7.20 | 90% watched marking and shortcut diagnostics; device testing pending |

Install **one add-on version plus Helper 0.2.7**. The test build does not fix SMB, shortcuts or stale-session recovery.

## Installation

1. Copy the Helper APK and your chosen add-on ZIP to a USB drive.
2. Install the Helper APK using Zidoo's File Manager. Existing users should update without uninstalling.
3. Open the Helper, test a **complete local movie filename** beginning with `/storage/`, then save a diagnostic report.
4. In Kodi, enable **Settings → System → Add-ons → Unknown sources**.
5. Choose **Add-ons → Install from zip file** and install the add-on ZIP. Do not select a source archive.
6. Fully close and reopen Kodi.
7. Scan the local media into Kodi's video library, then open **Movies, TV shows or Music videos** and select the item.
8. Exit playback normally so Kodi can receive the final resume position.

Native Zidoo resume is on by default. Watched marking uses the final position, including seeking: **95% in 0.7.19, 90% in 0.7.20**. Long-press should retain Kodi's context menu; eligible local library items offer **Play with Zidoo**.

[Complete installation instructions](downloads/Kodi%20for%20Zidoo%20install.txt) · [Test instructions](downloads/testing/README.md) · [Preview checksums](downloads/SHA256SUMS.txt)

## Compatibility and feedback

Tested on **Z30 Pro / firmware 1.3.45 / Android 11 / Kodi 22 beta2 ARM 32-bit**. A tester reports successful local-library playback, resume and watched marking on **Z9X 8K / firmware 1.3.45 / Kodi 22 beta2 ARM 32-bit / Arctic Horizon 2**. Home shortcuts failed to route to Zidoo in that test.

Other configurations, including Z9X Pro, original Z10, Kodi 20.2 and Maven builds, are unverified.

**Known return issue:** Kodi can restart during native playback and show Home before restoring the library list. See [Kodi issue #29691](https://github.com/xbmc/xbmc/issues/29691).

For a pending/queue message, record its exact wording and save a Helper diagnostic report before clearing data. Only discard a pending session when no Zidoo video is playing.

[Report test results or problems](https://github.com/CanesTR/Kodi-for-Zidoo/issues). Include model, firmware, Android version, exact Kodi build, skin, component versions, complete media path without credentials, and whether you used the library, Files or a widget. Report playback, resume, watched marking and return behavior. Never post passwords or credential XML files.

## Source and development

[0.7.19 source archive](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/Kodi-for-Zidoo-0.7.19-source.zip). Source folders: `addon_0.7.19/`, `addon_0.7.20/`, and `android-helper/`.

Run tests from the repository root:

```sh
python -m unittest discover -s tests_0.7.19
python -m unittest discover -s tests_0.7.20
```

The 0.7.20 build passed 21 automated tests; device testing is pending. Helper 0.2.7 is the existing signed APK. Forks should use their own signing key. Never commit signing keys, passwords, local.properties, user profiles or diagnostic logs.

Source archives and previously downloaded packages contain the instructions from their packaging date; this page and the linked installation text contain the latest guidance.
