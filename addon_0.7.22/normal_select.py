import sys
import xbmc
import xbmcgui
from default import ADDON, MEDIA, run, log
from media_path import supported, display_path


def route(kind, itemid, path, enabled=True, smb_enabled=False):
    if not enabled or kind not in MEDIA or not supported(path, smb_enabled):
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
    log('SELECTION METADATA window={} focus={} focused_type={!r} focused_id={!r} focused_path={!r} generic_type={!r} generic_id={!r} generic_path={!r}'.format(
        xbmcgui.getCurrentWindowId(), focus, kind, itemid, display_path(path),
        xbmc.getInfoLabel('ListItem.DBTYPE'), xbmc.getInfoLabel('ListItem.DBID'),
        display_path(xbmc.getInfoLabel('ListItem.FileNameAndPath'))))
    target = route(kind, itemid, path,
                   ADDON.getSetting('normal_play') != 'false', ADDON.getSettingBool('experimental_smb'))
    log('SELECTION window={} focus={} type={} id={} path={} routed={}'.format(
        xbmcgui.getCurrentWindowId(), focus, kind, itemid, display_path(path), bool(target)))
    if target:
        run(*target)
    else:
        action = 'Play' if len(sys.argv) > 1 and sys.argv[1] == 'play' else 'Select'
        # Action delivers directly to the window; it does not re-read the keymap.
        xbmc.executebuiltin('Action(' + action + ')')


if __name__ == '__main__':
    main()
