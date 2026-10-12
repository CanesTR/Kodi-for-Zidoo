# Experimental ZDMC launch: add-on 0.7.25 + Helper 0.2.11

**Source only: a signed Helper APK must be built before device testing.**

[Download Android Studio source package](Kodi-for-Zidoo-0.7.25-Helper-0.2.11-ZDMC-test-source.zip) · [Build and test instructions](Build-and-test.txt) · [Add-on ZIP](Kodi-for-Zidoo-0.7.25-ZDMC-launch-test.zip)

This opt-in S928-device experiment selects Zidoo's ZDMCActivity with play_mode=zdmc. The standard PlayerActivity mode is the default. It is not a confirmed fix for the Home-screen return transition.

Build Helper 0.2.11 with the existing signing key and install both components. First verify standard mode. Then enable **Experimental ZDMC launch** in the Helper, test standalone local playback, save the report, and test Kodi library playback, resume, watched marking and return. The Helper returns to official Kodi's org.xbmc.kodi package.

The experiment retains the current result relationship and zero task flags; it does not reproduce ZDMC's NEW_TASK/CLEAR_TASK handoff. Full session, file and time checks remain mandatory. Missing or incompatible results do not update the library. Use the recovery steps in the instructions if a session stays pending.

Validation: 35 add-on tests passed; Java syntax and XML parsed successfully. No Android build or device validation has been performed. The package contains no keystore, credentials, diagnostic logs or APK.
