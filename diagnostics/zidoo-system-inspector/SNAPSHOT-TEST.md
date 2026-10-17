# Caller snapshot — Inspector 0.1.1

This is a read-only visibility probe, not a playback fix. It does not stop apps or change Android settings. It does not need another movie test.

1. Uninstall only **Zidoo System Inspector 0.1.0**, because the Actions build uses a fresh test signing key. Leave Kodi, KodiZidooDiagnostic and the Bridge Helper installed.
2. Download the successful **Zidoo-System-Inspector-0.1.1** Actions artifact, extract it, and install `app-debug.apk`.
3. Open **Zidoo System Inspector** and choose **Save caller snapshot (small)**. Keep the app open until it reports the saved filename.
4. Send the `zidoo-caller-snapshot-....txt` file from **Internal storage/Download/ZidooSystemInspector**. Do not select the large APK export again.

The report tries fixed read-only `ps` process listings and reads the current cmdline/stat files for PIDs 2290, 12575 and 28398 from the uploaded exit reports. Android may block all of these. It also records the inspector-visible process API result, package UIDs and declared process names for stop-capable system packages, selected Zidoo audio/video properties, uptime and framework JAR filenames. Current process names may reveal other running applications. It does not collect media paths, credentials, app data or unrestricted property dumps. Command output is capped at 64 KiB and each command times out after three seconds.

A current mapping is a lead, not proof of who owned a historical PID. Reboots and PID reuse matter. Empty lists, inaccessible proc files and command failures are explicitly inconclusive; the app does not bypass Android process restrictions. A package's stopped flag is not proof that no shared process or service exists.

## Current evidence

On 2026-10-17 the diagnostic Kodi survived some Home-only, File Explorer-only and one native playback interval. A later playback test ended PID 23457 at 17:00:36 local time with reason 10 and `stop ... due to from pid 28398`; Kodi restarted at 17:02:29. Tom reports Music Player remained stopped. Regular Kodi also restarted during two SMB sessions, with bridge PIDs 2628 -> 4910 -> 6125. These results do not establish Music Player as the caller.

The uploaded firmware APKs contain a Music Player audio transition manager that can force-stop non-exempt prior audio apps; ZDMC is explicitly exempt there. That is a concrete code lead, not a proven explanation of the observed stops. The Settings whitelist identified in the export is labelled **Third-party APP frame rate whitelist** and must not be described as a background-app exemption. ClearManager also contains a force-stop call, but its presence is not evidence that it executed during playback.

Validation: Java syntax parsing locally; Actions must additionally pass Android compilation, lint and APK signature verification before installation. No native Kodi rebuild is triggered by this project.
