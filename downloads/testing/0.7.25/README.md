# Experimental ZDMC launch: add-on 0.7.25 + Helper 0.2.11

**Z30 Pro test result (12 October 2026): leave Experimental ZDMC launch OFF.** Experimental mode played local media but returned result code 0 with no result data, so resume/watched updates were correctly rejected. SMB attempts returned immediately without confirmed playback. Kodi still restarted. Use the standard PlayerActivity mode; this experiment has not solved the return transition.

**[Download the complete tester package](Kodi-for-Zidoo-0.7.25-Helper-0.2.11-test-package.zip)** · [Installation and test instructions](Kodi-for-Zidoo-test.txt)

Includes the signed Helper 0.2.11 APK, add-on 0.7.25 ZIP and test instructions. Android Studio is not required to install this package. Update both components without uninstalling Kodi or clearing its data.

This opt-in S928-device experiment selects Zidoo's ZDMCActivity with play_mode=zdmc. The standard PlayerActivity mode is the default. It is not a confirmed fix for the Home-screen return transition.

First verify standard mode. Then enable **Experimental ZDMC launch** in the Helper, test standalone local playback, save the report, and test Kodi library playback, resume, watched marking and return. The Helper returns to official Kodi's org.xbmc.kodi package; the separately installed Maven build is not the return target.

The experiment retains the current result relationship and zero task flags; it does not reproduce ZDMC's NEW_TASK/CLEAR_TASK handoff. Full session, file and time checks remain mandatory. Missing or incompatible results do not update the library. Follow the recovery steps if a session stays pending.

Validation: 35 add-on tests passed. The uploaded APK reports version 0.2.11 / versionCode 14 and the same package and signing certificate as previous Helper builds. Its V1 signature, manifest and signed-entry digests verified successfully. Experimental and standard launch markers are present. Device testing is pending.

Separate downloads: [Signed APK](Kodi-for-Zidoo-Helper-0.2.11.apk) · [Add-on ZIP](Kodi-for-Zidoo-0.7.25-ZDMC-launch-test.zip) · [Source package](Kodi-for-Zidoo-0.7.25-Helper-0.2.11-ZDMC-test-source.zip) · [Build instructions](Build-and-test.txt) · [Checksums](SHA256SUMS.txt)
