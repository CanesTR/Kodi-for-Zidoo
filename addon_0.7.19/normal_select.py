import sys
import xbmc
import xbmcgui
from default import ADDON, MEDIA, run, log


def route(kind, itemid, path, enabled=True):
    if not enabled or kind not in MEDIA or not path.startswith('/storage/'):
        return None
    try:
        value = int(itemid)
    except (TypeError, ValueError):
        return None
    return (value, kind) if value >= 0 else None


def main():
    # Read the focused container, so sidebar buttons never launch its old selection.
    focus = xbmcgui.Window(xbmcgui.getCurrentWindowId()).getFocusId()
    prefix = 'Container({}).ListItem.'.format(focus)
    kind = xbmc.getInfoLabel(prefix + 'DBTYPE')
    itemid = xbmc.getInfoLabel(prefix + 'DBID')
    path = xbmc.getInfoLabel(prefix + 'FileNameAndPath')
    target = route(kind, itemid, path,
                   ADDON.getSetting('normal_play') != 'false')
    log('SELECTION window={} focus={} type={} id={} path={} routed={}'.format(
        xbmcgui.getCurrentWindowId(), focus, kind, itemid, path, bool(target)))
    if target:
        run(*target)
    else:
        action = 'Play' if len(sys.argv) > 1 and sys.argv[1] == 'play' else 'Select'
        # Action delivers directly to the window; it does not re-read the keymap.
        xbmc.executebuiltin('Action(' + action + ')')


if __name__ == '__main__':
    main()
