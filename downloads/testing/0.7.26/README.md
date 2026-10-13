# Return diagnostics: add-on 0.7.26

[Download add-on ZIP](Kodi-for-Zidoo-0.7.26-return-diagnostics.zip)

Kodi for Zidoo 0.7.26: return diagnostics

Use your existing signed Helper 0.2.11. Leave Experimental ZDMC launch OFF.
This add-on adds process-ID and return-window logging only. It does not
change playback, resume, watched marking or return navigation behavior.

1. Install this add-on ZIP through Kodi > Add-ons > Install from zip file.
2. Fully close and reopen Kodi once after installing.
3. Play one local movie for about 30 seconds, then exit normally.
4. Repeat with the same movie for a few minutes, then with an SMB movie.
5. Record the movie title, approximate exit time and whether the return went
   directly to the list or showed Home first.
6. Save zidoo_bridge_diagnostic.log and Kodi's kodi.log / kodi.old.log.
   If a direct return occurs, save the logs before further playback so the
   relevant Kodi startup log is not rotated away.

RETURN PROCESS compares Kodi's process ID at launch and at the verified
return. The window/folder logs distinguish list preservation from restoration.
No new Helper APK or Kodi reinstall is required.

Validation: all 35 add-on tests passed. Device testing is pending. This is diagnostic logging, not a confirmed Home-transition fix.
