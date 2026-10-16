# Separate diagnostic Kodi: exit-reason logging

Status: source and build workflow prepared. No successful APK build or device test yet.

[GitHub build runs](https://github.com/CanesTR/Kodi-for-Zidoo/actions/workflows/kodi-diagnostic.yml) · [Test instructions](TESTING.md)

This experiment builds ARM32 Kodi 22 beta2 at commit
`e513e0ff4331fc25fd2454659a9dd3e6b7670146`, the exact revision in Tom's logs.
`apply.py` refuses a different revision or a modified Java template. It adds
best-effort lifecycle and own-process ApplicationExitInfo logging, plus automatic
Downloads report export. It uses a separate app name/package/data directory;
working Kodi and the bridge packages remain unchanged.

The first test uses Android Home -> Zidoo File Explorer -> native playback ->
reopen the diagnostic app. No Helper changes, ADB or developer options are needed.
Changing package identity may affect firmware behavior, so the result must be
compared carefully with org.xbmc.kodi. A different result is evidence, not a fix.

The GitHub workflow runs manually or on changes to this experiment/workflow.
It builds Kodi's native dependencies and APK from source, using the pinned source's
Android build guide (NDK 28c, SDK/build tools 37). A full first build can take hours
and may need toolchain/build corrections. The job has a six-hour limit. No binary
add-ons are built because they are unnecessary for the initial lifecycle test.

The runner creates an ephemeral test-only signing key. No existing Helper key or
Kodi signing key is requested or used. The signing key is not published. Successful
APKs and checksums are uploaded as a 14-day Actions artifact, not a public release.
Never install an APK from a failed or incomplete run. Future test APKs signed with
a different ephemeral key may require uninstalling only the separate diagnostic app.

Validation performed locally: three patch tests passed (actual pinned template
parses after patching; wrong revision/modified source refused; repeat patch
refused), and workflow YAML parsed. This does not substitute for Android/native
compilation or device tests.

## Provenance

Kodi source and baseline templates: xbmc/xbmc at the pinned commit above.
Kodi is GPL-2.0-or-later; see COPYING and upstream LICENSES/README.md for additional
licenses. Diagnostic modifications in this directory are GPL-2.0-or-later.
The build fetches complete upstream source rather than shipping a modified binary
without source. Workflow and patch files provide the experiment's build recipe.
