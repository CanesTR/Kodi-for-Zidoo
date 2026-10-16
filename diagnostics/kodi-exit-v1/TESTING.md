# Kodi process-exit diagnostic v1

**Build preparation, not a finished APK.** The workflow must finish successfully before installation.

This uses the exact Kodi 22 beta2 revision from the existing test logs:
`e513e0ff4331fc25fd2454659a9dd3e6b7670146`, ARM 32-bit.

The package is `com.stormtracker.kodidiagnostic`, displayed as KodiZidooDiagnostic.
It is separately signed with a temporary test key, and uses its own app data.
Do not uninstall working Kodi, copy its database, or install this over it.
Future separately signed diagnostic builds may require uninstalling only this test app.

## First test: no Helper or add-on required

1. Install the APK from the completed GitHub Actions artifact.
2. Open KodiZidooDiagnostic once, leave default Estuary and default settings.
3. Press Android Home and open Zidoo File Explorer.
4. Play a known local movie for approximately 30 seconds, then exit normally.
5. Reopen KodiZidooDiagnostic from Android's app screen. Wait 10 seconds.
6. Open Internal storage/Download/KodiZidooDiagnostics and send the newest
   `kodi-process-exit-...txt` report. Also note the movie and approximate exit time.
7. Repeat with an SMB movie and, as a control, with File Explorer but no playback.

Reports are written on activity creation. If the app simply resumes in the same
process, there may be no new Downloads report. In that case, quit the diagnostic
app normally and reopen it once to export the accumulated lifecycle events;
note that manual quit so it is not confused with playback-related termination.
Do not force-stop or clear app data before collecting reports.

The first run may contain zero exit records. After a process death, Android may
report crash/native crash, low memory, a signal, self-exit or another reason.
A signal or generic system reason may still need additional investigation.
Firmware may omit records. A separate package may behave differently from
org.xbmc.kodi; survival here would not prove the official package's issue is fixed.

The existing Helper returns to org.xbmc.kodi, so do not install the bridge add-on
in this test app for the initial test. Independent native playback already
reproduced the restart in the earlier Maven comparison.

## Implementation and limits

The patch adds best-effort lifecycle/file logging and reads only this APK's
Android 11+ ApplicationExitInfo. It does not request DUMP, root or ADB, change
playback, add a foreground service, keep the process alive, or change task flags.
Reports contain process IDs, timestamps, lifecycle events and Android's own
exit descriptions/memory samples, not video filenames or credential files.
Historical records can repeat in successive exported reports.

A single worker serializes file writes and exports. Very late lifecycle writes
may be lost if Android kills the process immediately. Android's recorded exit
history is the primary evidence. The local report rotates at about 256 KiB
(two files); each startup makes one new Downloads snapshot. These snapshots can
be deleted after analysis. No traces/tombstones are collected in this v1 build.

This is a full native Kodi build, not an Android Studio Helper build. Native
compilation and dependencies can take hours. It has not yet been device-tested.
