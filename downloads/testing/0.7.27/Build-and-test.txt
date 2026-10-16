Kodi for Zidoo 0.7.27 + Helper 0.2.12: SMB filename hash test

This source package includes the full Android Studio Helper project and the
installable Kodi add-on ZIP. No signed APK is included yet.

BUILD HELPER 0.2.12
1. Extract this package completely on your PC.
2. Android Studio > File > Open > select the extracted android-helper folder.
   Open the folder, not app/build.gradle.
3. Let Gradle sync. Version is 0.2.12 / versionCode 15.
4. Build > Generate Signed Bundle / APK > APK.
5. Use the SAME keystore and key alias as your previous Helper builds.
6. Select release and finish, then install the APK as an update on the Zidoo.
   Do not uninstall the Helper, clear Kodi data, or change signing keys.

If needed, keep your existing working Gradle/plugin versions. Replace BOTH
DiagnosticActivity.java and MediaPath.java in your working project's
app/src/main/java/com/stormtracker/zidoobridge/ folder. Set app/build.gradle
to versionCode 15 and versionName '0.2.12'. The manifest is unchanged.

INSTALL AND TEST
1. Install the new signed Helper 0.2.12 APK.
2. In Kodi > Add-ons > Install from zip file, install
   Kodi-for-Zidoo-0.7.27-SMB-hash-test.zip from this package.
   Do not install this whole source archive into Kodi.
3. Fully close and reopen Kodi once. Keep current SMB and NAS mapping settings.
4. In the Helper leave Experimental ZDMC launch OFF.
5. First test an ordinary local movie and an ordinary SMB movie.
6. Test the original #Chef library entry without renaming its file or folders.
   Literal # and URL-encoded %23 hashes are supported in subfolders/filenames.
   No library rescan should be needed.
7. Check native playback, native resume, the saved Kodi resume position, and
   automatic watched marking at a final position of 90%.
8. If available, test a different movie containing # and a TV episode via SMB.
9. Save the Helper report plus Kodi's kodi.log and kodi.old.log, noting whether
   playback started from the library or a shortcut.

This is a path-handling test, not a fix for Kodi restarting or the Home flash.
No shortcut routing or skin changes are included.
Credentials, ports, query strings, invalid path segments and # in share names
remain unsupported. Full session/host/share/folder/file/time result validation
is retained. Raw # within an SMB file path is treated as filename text, not as
a URL fragment. Encoded escapes are decoded once; %2523 differs from %23.

Reports are saved in Internal storage/Download/ZidooBridge.
If a pending session remains, close the native player, stop diagnostic polling,
wait for it to stop, then reset the pending session while the player is idle.
