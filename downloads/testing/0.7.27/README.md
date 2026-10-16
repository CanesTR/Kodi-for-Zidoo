# SMB filename hash test: add-on 0.7.27 + Helper 0.2.12

**[Download the complete tester package](Kodi-for-Zidoo-0.7.27-Helper-0.2.12-test-package.zip)** · [Installation and test instructions](Kodi-for-Zidoo-test.txt)

Includes the signed Helper 0.2.12 APK, add-on 0.7.27 ZIP and instructions. Android Studio is not required for installation.

[Download complete Android Studio source package](Kodi-for-Zidoo-0.7.27-Helper-0.2.12-SMB-hash-source.zip) · [Build and test instructions](Build-and-test.txt) · [Add-on ZIP](Kodi-for-Zidoo-0.7.27-SMB-hash-test.zip)

Fixes parsing of literal `#` characters in SMB subfolders and filenames, including thieryal's `#Chef` path in [issue #2](https://github.com/CanesTR/Kodi-for-Zidoo/issues/2). No renaming or library rescan should be needed. Install both new components as updates, without clearing Kodi data. Keep Experimental ZDMC launch OFF.

First verify ordinary local and SMB playback, then the original `#Chef` library entry, native resume and Kodi resume/watched updates. Submit the Helper report and Kodi logs with the test result. This has not yet been validated on a Zidoo device.

Full result-identity checks remain intact. Credentials, ports, queries, traversal paths and hash characters in share names remain unsupported. Literal hashes in SMB file paths are filename data; encoded escapes are decoded once. The native SMB URI sends hashes as `%23` while the original library identity is preserved.

Validation: 37 Python tests passed; Java MediaPath compiled and its test harness passed, including the exact tester path, encoded hashes, alias mapping, local paths, wrong-file rejection and unsafe-path rejection. All Helper Java source parsed. The uploaded APK reports version 0.2.12 / versionCode 15, matches the previous signing certificate, and passed V1 signature and all signed-payload digest checks. The hash escaping is present in both relevant bytecode methods. Device testing is pending.

The Home-screen transition and restart remain unresolved. No skin or shortcut-routing behavior is changed. The source package contains no signing key or credentials.

[Signed APK](Kodi-for-Zidoo-Helper-0.2.12.apk) · [Checksums](SHA256SUMS.txt)
