"""Save and restore the library location across an external-player handoff."""
import json
import time
import xbmc
import xbmcgui


def capture():
    try:
        window = xbmcgui.getCurrentWindowId()
        if window != 10025:
            return None
        control = xbmcgui.Window(window).getFocusId()
        folder = xbmc.getInfoLabel('Container.FolderPath')
        if not folder.startswith(('videodb://', '/storage/')):
            return None
        prefix = 'Container({}).'.format(control)
        selected = xbmc.getInfoLabel(prefix + 'ListItem.DBID')
        kind = xbmc.getInfoLabel(prefix + 'ListItem.DBTYPE')
        if not selected.isdigit() or kind not in ('movie', 'episode', 'musicvideo'):
            return None
        next_id = xbmc.getInfoLabel(prefix + 'ListItem(1).DBID')
        next_kind = xbmc.getInfoLabel(prefix + 'ListItem(1).DBTYPE')
        return {'window': window, 'control': control, 'folder': folder,
                'selected': selected, 'kind': kind,
                'next': next_id if next_kind == kind and next_id != selected else ''}
    except Exception:
        return None


def open_folder(context, monitor):
    if not context or context.get('window') != 10025:
        return
    folder = context.get('folder', '')
    if not folder.startswith(('videodb://', '/storage/')):
        return
    # Wait briefly for Kodi's startup or return animation to finish.
    for _ in range(100):
        current = xbmcgui.getCurrentWindowId()
        if current in (10000, 10025) and not xbmc.getCondVisibility('Window.IsActive(startup)'):
            break
        if monitor.waitForAbort(0.1):
            return
    else:
        return
    if current == 10025 and xbmc.getInfoLabel('Container.FolderPath') != folder:
        return  # Respect navigation the user has already made.
    if current == 10000:
        xbmc.executebuiltin('ActivateWindow(10025,{},return)'.format(json.dumps(folder)))
    return True


def restore(context, watched, monitor):
    if not open_folder(context, monitor):
        return
    folder = context['folder']
    control = int(context['control'])
    target = context.get('next') if watched and context.get('kind') == 'episode' else context.get('selected')
    target = target or context.get('selected')
    for _ in range(20):
        if monitor.abortRequested():
            return
        if xbmcgui.getCurrentWindowId() != 10025:
            if monitor.waitForAbort(0.25): return
            continue
        if xbmc.getInfoLabel('Container.FolderPath') != folder:
            if monitor.waitForAbort(0.25): return
            continue
        prefix = 'Container({}).'.format(control)
        try:
            count = min(int(xbmc.getInfoLabel(prefix + 'NumItems')), 2000)
        except (ValueError, TypeError):
            count = 0
        for index in range(count + 1):
            item = prefix + 'ListItemAbsolute({}).'.format(index)
            if xbmc.getInfoLabel(item + 'DBID') == target and xbmc.getInfoLabel(item + 'DBTYPE') == context.get('kind'):
                xbmc.executebuiltin('SetFocus({},{},absolute)'.format(control, index))
                return
        if monitor.waitForAbort(0.25): return
