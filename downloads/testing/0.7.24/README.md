# Return timing experiment

Uses existing signed Helper 0.2.10. Install the 0.7.24 add-on ZIP inside Kodi, then fully close/reopen Kodi. Keep your current SMB and hostname mapping settings.

While a bridge session is pending, the service checks for a final result every 0.1 seconds instead of every 2 seconds. Idle checking remains every 2 seconds. Playback and result validation are unchanged. This may reduce a return-time polling delay; it does not prevent Kodi process restart or promise to eliminate Home.

Compare a local and SMB playback return against 0.7.23. Report how long Home remains visible and save fresh Kodi/bridge logs. Reinstall 0.7.23 if no benefit. 34 automated add-on tests passed; actual transition improvement needs device testing.
