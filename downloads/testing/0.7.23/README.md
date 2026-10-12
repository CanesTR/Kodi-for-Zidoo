# Hostname-mapping test: add-on 0.7.23 + Helper 0.2.10

[Download complete test package](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/testing/0.7.23/Kodi-for-Zidoo-0.7.23-Helper-0.2.10-test-package.zip)

Individual components:
- [Signed Helper 0.2.10 APK](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/testing/0.7.23/Kodi-for-Zidoo-Helper-0.2.10.apk)
- [Add-on 0.7.23 ZIP](https://raw.githubusercontent.com/CanesTR/Kodi-for-Zidoo/main/downloads/testing/0.7.23/Kodi-for-Zidoo-0.7.23-test.zip)
- [Checksums](SHA256SUMS.txt)
- [Source](https://github.com/CanesTR/Kodi-for-Zidoo/tree/smb-hostname-test)

## Install and configure

1. Extract the outer package. Update the Zidoo with Helper 0.2.10 APK.
2. Open the Helper, allow storage permission on Android 6–9 if requested, then save a diagnostic report.
3. Install the separate add-on ZIP inside Kodi and fully close/reopen Kodi.
4. Open Kodi for Zidoo > Configure. Enable **Test SMB library playback**.
5. For a hostname-based NAS source that Zidoo returns as an IP mount, set:
   - **NAS hostname to map:** the hostname in Kodi's SMB URL (host only).
   - **That NAS IPv4 address:** the current address of the same NAS.
6. Confirm the address in NAS/router settings or the Helper playback report. Do not guess the mapping.
7. Leave BOTH fields empty if mapping is unnecessary. The configured mapping applies only to that hostname.
8. Select a scanned library movie, episode or music video. Confirm Zidoo File Explorer already plays the NAS file using its saved login.

No library rescan or change to existing source paths is needed.
This is one explicit mapping, not automatic hostname discovery. If the NAS IP changes, update it before another launch.
Direct-IP SMB URLs and local /storage/ paths remain supported. SMB URLs with embedded credentials are rejected.

## What to test

- Launch a hostname-based SMB movie from Kodi's Movies library.
- Exit after a short period; check the Kodi resume bookmark and return to the saved list.
- Play again; check native Zidoo resume.
- Exit below 90% and check resume; at 90% or above check automatic watched marking. Seeking counts toward final position.
- Repeat with a TV episode, a direct-IP NAS file and a local /storage/ file.
- If rejected, save the Helper report and Kodi bridge log before clearing data.

The launch session pins the mapped host and full share/folder/file identity.
Both Helper and add-on validate it before resume/watched updates; the result must echo the launch mapping.
Unexpected IPs, shares, folders or filenames are rejected.
No passwords are imported or stored by the bridge.

SMB playback from Kodi was confirmed to launch on Z30 Pro, but hostname-based returned IPs were rejected by the prior build.
This build addresses that rejection; resume/watched updates still need device validation.
Kodi's restart/Home return issue and widget/Files limitations remain.
Use the Helper test buttons only for standalone diagnostics, not to configure Kodi routing.

APK verified as Helper 0.2.10 / versionCode 13. Signature and signed entry digests checked; signing certificate matches prior Helpers.
34 automated add-on tests passed. No device test is claimed for this package.
Report model, firmware, Android version, Kodi build, skin, exact messages and both component versions.
Review logs before sharing; never post passwords or credential XML files.
