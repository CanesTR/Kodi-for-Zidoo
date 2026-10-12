# SMB integration test: add-on 0.7.22 + Helper 0.2.9

[Download complete tester package](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/testing/0.7.22/Kodi-for-Zidoo-0.7.22-Helper-0.2.9-test-package.zip)

Individual components:
- [Signed Helper 0.2.9 APK](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/testing/0.7.22/Kodi-for-Zidoo-Helper-0.2.9.apk)
- [Add-on 0.7.22 ZIP](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/testing/0.7.22/Kodi-for-Zidoo-0.7.22-test.zip)
- [Checksums](SHA256SUMS.txt)
- [Source and build notes](https://github.com/CanesTR/Kodi-for-Zidoo/tree/smb-library-test)

## Installation

1. Extract the outer package. Install the Helper APK on Zidoo as an update.
2. Open Helper 0.2.9, allow storage permission on Android 6–9 and save a diagnostic report.
3. Install the enclosed add-on ZIP inside Kodi through Add-ons → Install from zip file. Do not select the outer package.
4. Fully close and reopen Kodi.
5. Open Kodi for Zidoo add-on settings and enable **Test SMB library playback**. This setting is OFF by default.
6. Confirm the NAS video plays in Zidoo File Explorer using its saved login.
7. Select a scanned item from Kodi's Movies, TV shows or Music videos library.

Use BOTH components. Helper 0.2.8 cannot perform SMB library sessions.
Users do not need Android Studio or a path mapping in the Helper.

## SMB path requirements

Use a complete credential-free smb://host/share/folder/movie.mkv library path.
Kodi credentials must be stored separately; login/password URLs are rejected.
Host and share names, folder case, filename, spaces and Unicode are preserved.
Explicit ports, IPv6 hosts, query strings, fragments, dot traversal and encoded path separators are not supported.
The integration uses Zidoo's saved NAS connection; it does not import passwords or create mounts.

The tester's Z9X 8K report confirmed standalone SMB launch with saved credentials and successful final native results.
This build now tests Kodi-integrated playback. It accepts a returned mount path only when the complete host/share/folder/filename matches:
smb://host/share/folder/file → /mnt/smb/host#share/folder/file.
Unexpected return paths leave the library unchanged.

## Test sequence

1. Play one NAS movie from the library and exit after a short period. Check Kodi's resume bookmark.
2. Play it again and check native Zidoo resume.
3. Exit below 90% and check the bookmark; exit at 90% or above and check automatic watched marking. Seeking counts toward the final position.
4. Repeat with a different NAS movie, a TV episode and a local /storage/ file.
5. Check return to Kodi and pending-session recovery if necessary. Kodi may still restart during native playback.
6. Save Helper and Kodi logs if a step fails; include exact messages and model, firmware, Android version, Kodi build and skin. Review logs before sharing and do not post credentials.

Home shortcuts/widgets, Videos → Files and arbitrary add-on streams remain outside this test.
The separate Helper SMB diagnostic button still does not update Kodi's library.
Android 6–9 export support and idle-guarded pending-session reset are retained.

APK verified as Helper 0.2.9, versionCode 12, min SDK 23, target SDK 28.
Its v1 signature and signed entry digests were checked; signing certificate matches previous Helpers.
31 automated add-on tests passed and Python/Java syntax checks passed.
Integrated SMB playback, resume and watched behavior require device testing.
The regular public preview remains 0.7.19 + Helper 0.2.7.
