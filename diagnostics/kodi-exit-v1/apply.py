#!/usr/bin/env python3
"""Apply diagnostic-only changes to the exact tested Kodi revision."""
from pathlib import Path
import subprocess
import sys

PIN = 'e513e0ff4331fc25fd2454659a9dd3e6b7670146'
root = Path(sys.argv[1]).resolve()
bundle = Path(__file__).resolve().parent
head = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
if head != PIN:
    raise SystemExit('Refusing to patch a different Kodi revision: ' + head)
main = root / 'tools/android/packaging/xbmc/src/Main.java.in'
source = main.read_text()
if source != (bundle / 'upstream-Main.java.in').read_text():
    raise SystemExit('Main.java.in differs from the reviewed source; refusing to overwrite it')
# Keep Kodi native startup ordering and all lifecycle super calls unchanged.
source = source.replace('    super.onCreate(savedInstanceState);',
    '    super.onCreate(savedInstanceState);\n    recordExitDiagnostic("onCreate", true);', 1)
for name in ('onStart', 'onResume', 'onPause', 'onDestroy'):
    anchor = '    super.' + name + '();'
    if source.count(anchor) != 1:
        raise SystemExit('Unexpected lifecycle anchor: ' + name)
    source = source.replace(anchor, '    recordExitDiagnostic("' + name + '", false);\n' + anchor, 1)
# Main has no Java onStop override in this revision.
anchor = '  @Override\n  public void onDestroy()'
source = source.replace(anchor,
    '  @Override\n  public void onStop()\n  {\n    recordExitDiagnostic("onStop", false);\n    super.onStop();\n  }\n\n' + anchor, 1)
source = source.rstrip()[:-1] + '\n' + (bundle / 'logger.java.inc').read_text() + '\n}\n'
version = root / 'version.txt'
original_version = version.read_text()
if 'APP_NAME Kodi\n' not in original_version or 'APP_PACKAGE org.xbmc.kodi\n' not in original_version:
    raise SystemExit('Unexpected app identity in version.txt')
main.write_text(source)
version.write_text(original_version.replace('APP_NAME Kodi\n', 'APP_NAME KodiZidooDiagnostic\n')
    .replace('APP_PACKAGE org.xbmc.kodi\n', 'APP_PACKAGE com.stormtracker.kodidiagnostic\n'))
print('Applied diagnostic logging; separate package com.stormtracker.kodidiagnostic')
