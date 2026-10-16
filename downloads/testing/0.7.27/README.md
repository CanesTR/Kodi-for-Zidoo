# SMB filename hash test: add-on 0.7.27 + Helper 0.2.12

**Source only: build the signed Helper APK before testing.**

[Download complete Android Studio source package](Kodi-for-Zidoo-0.7.27-Helper-0.2.12-SMB-hash-source.zip) · [Build and test instructions](Build-and-test.txt) · [Add-on ZIP](Kodi-for-Zidoo-0.7.27-SMB-hash-test.zip)

Fixes parsing of literal `#` characters in SMB subfolders and filenames, including thieryal's `#Chef` path in [issue #2](https://github.com/CanesTR/Kodi-for-Zidoo/issues/2). No renaming or library rescan should be needed. Build Helper 0.2.12 using the existing signing key and install both components. Keep Experimental ZDMC launch OFF.

First verify ordinary local and SMB playback, then the original `#Chef` library entry, native resume and Kodi resume/watched updates. Submit the Helper report and Kodi logs with the test result. This has not yet been validated on a Zidoo device.

Full result-identity checks remain intact. Credentials, ports, queries, traversal paths and hash characters in share names remain unsupported. Literal hashes in SMB file paths are filename data; encoded escapes are decoded once. The native SMB URI sends hashes as `%23` while the original library identity is preserved.

Validation: 37 Python tests passed; Java MediaPath compiled and its test harness passed, including the exact tester path, encoded hashes, alias mapping, local paths, wrong-file rejection and unsafe-path rejection. All Helper Java source parsed. The Android APK has not been built or device-tested here.

The Home-screen transition and restart remain unresolved. No skin or shortcut-routing behavior is changed. The source package contains no signing key or credentials.
