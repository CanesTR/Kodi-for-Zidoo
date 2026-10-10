# 0.7.20 test build

Requires the existing signed Helper 0.2.7. Install this ZIP inside Kodi and fully restart Kodi. No Helper reinstall or APK rebuild is needed.

Automatic watched marking changes to 90% of the final playback position. Seeking counts toward this threshold. Validated native results are still required.

Shortcut selection diagnostics now record focused and generic item metadata in the Kodi log. Shortcut routing behavior is unchanged; this build does not claim to fix widgets or shortcuts.

Test a local library movie at just below 90% and at 90% or above. Confirm resume below the threshold and watched marking above it. Then enable Kodi debug logging, try a local movie through the failing home shortcut, and save the Kodi log. Logs can include media paths; review before sharing.

If the pending/queue message recurs, record the exact message and export a Helper diagnostic report before clearing app data. Session recovery is unchanged pending that evidence.

SMB/NAS paths are not supported. Kodi may restart during native playback. This test build passed 21 automated tests; device testing is pending.
