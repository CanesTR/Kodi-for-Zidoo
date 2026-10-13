import time
import json
import os
import xbmc
import xbmcvfs
from default import PROFILE, NAME, PENDING, log, process_pending
import xbmcgui
from normal_keymap import sync
from return_navigation import restore, open_folder
from external_handoff import sync as sync_external, close_session

xbmcvfs.mkdirs(PROFILE)
monitor = xbmc.Monitor()
last_error = None
last_report = 0
log('SERVICE START ' + json.dumps({'addon': '0.7.26', 'kodi_pid': os.getpid(),
    'window': xbmcgui.getCurrentWindowId()}))
try:
    while not monitor.abortRequested():
        try:
            sync_external()
            payload = process_pending(on_return=lambda context: open_folder(context, monitor))
            sync()
            if payload:
                close_session(payload)
                try:
                    restore(payload.get('return_context'), payload.get('watched_marked'), monitor)
                    log('RETURN NAVIGATION FINISHED ' + json.dumps({'session': payload.get('session'),
                        'kodi_pid': os.getpid(), 'window': xbmcgui.getCurrentWindowId(),
                        'folder': xbmc.getInfoLabel('Container.FolderPath')}))
                except Exception as navigation_error:
                    log('RETURN NAVIGATION ERROR ' + repr(navigation_error))
            last_error = None
        except Exception as exc:
            message = str(exc)
            now = time.monotonic()
            if message != last_error or now - last_report >= 60:
                log('BACKGROUND ERROR ' + repr(exc))
                if isinstance(exc, ValueError):
                    xbmcgui.Dialog().notification(NAME, 'Result rejected; see diagnostic log')
                last_error = message
                last_report = now
        # Check promptly during a handoff; keep idle work at its previous rate.
        if monitor.waitForAbort(0.1 if os.path.exists(PENDING) else 2):
            break
finally:
    try:
        sync(False)
    except Exception as exc:
        log('KEYMAP CLEANUP ERROR ' + repr(exc))
