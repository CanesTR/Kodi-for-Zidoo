import time
import xbmc
import xbmcvfs
from default import PROFILE, NAME, log, process_pending
import xbmcgui
from normal_keymap import sync
from return_navigation import restore, open_folder
from external_handoff import sync as sync_external, close_session

xbmcvfs.mkdirs(PROFILE)
monitor = xbmc.Monitor()
last_error = None
last_report = 0
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
        if monitor.waitForAbort(2):
            break
finally:
    try:
        sync(False)
    except Exception as exc:
        log('KEYMAP CLEANUP ERROR ' + repr(exc))
