Kodi for Zidoo install.txt
Preview: add-on 0.7.21 / Helper 0.2.7

You need Kodi already installed on your Zidoo. This package does not include Kodi.
Tested on Zidoo Z30 Pro, firmware v1.3.45, Android 11, Kodi 22 BETA2 (32-bit).
Other Zidoo models and Kodi versions have not been verified.

1. Copy Kodi-for-Zidoo-Helper-0.2.7.apk and Kodi-for-Zidoo-0.7.21.zip to a USB drive.
2. On Zidoo open File Manager, select the APK and install Kodi for Zidoo Helper.
   If Android asks to allow installation from this source, allow it to continue.
   Existing testers should install it as an update, without uninstalling Helper.
3. Open Kodi. Go to Settings > System > Add-ons and enable Unknown sources
   if needed to install this add-on ZIP.
4. Go to Add-ons > Install from zip file and select Kodi-for-Zidoo-0.7.21.zip.
   Do not select the outer release package or source ZIP.
5. Fully close and reopen Kodi.
6. Choose a movie, episode or music video from your Kodi video library and
   press OK/Select or Play. Zidoo's native player should open automatically.
7. Exit the video normally. Kodi receives the final resume position.

Native Zidoo resume is enabled by default. Watched marking is automatic when
final playback position reaches at least 90 percent; there is no watched switch.
Long-press still opens Kodi's context menu. Play with Zidoo is also available.
The integration targets library items; arbitrary add-on streams are not verified.

KNOWN ISSUE
Kodi 22 can restart while Zidoo plays video. On return, Home may appear before
the saved library list is restored. ZDMC comparison tests retain the running app.
Reported at https://github.com/xbmc/xbmc/issues/29691
This preview does not fix that restart. It requires a separate Android Helper.

Existing testers: 0.7.21 removes the experimental Python handoff option and
cleans up only bridge-owned test player rules. Native playback uses the working
direct handoff. Existing unrelated player rules are preserved.
If a failed launch leaves a pending session, only discard it when no Zidoo
video is playing. Do not repeatedly launch videos while a session is pending.
