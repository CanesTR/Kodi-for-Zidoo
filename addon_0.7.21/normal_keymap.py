import os
import xbmc
import xbmcvfs
from default import ADDON

MARKER = '<!-- Zidoo Bridge owns this file -->'
PATH = xbmcvfs.translatePath('special://profile/keymaps/zz-zidoo-bridge.xml')
SCRIPT = 'special://home/addons/plugin.program.zidoo.bridge.diagnostic/normal_select.py'
VIDEO_XML = '<keymap>' + MARKER + '<videos><keyboard><return>RunScript(' + SCRIPT + ')</return><enter>RunScript(' + SCRIPT + ')</enter><play>RunScript(' + SCRIPT + ',play)</play><p>RunScript(' + SCRIPT + ',play)</p><return mod="longpress">ContextMenu</return><enter mod="longpress">ContextMenu</enter></keyboard><remote><select>RunScript(' + SCRIPT + ')</select><play>RunScript(' + SCRIPT + ',play)</play><select mod="longpress">ContextMenu</select></remote></videos></keymap>'
XML = VIDEO_XML.replace('</keymap>', VIDEO_XML[VIDEO_XML.index('<videos>'):VIDEO_XML.index('</videos>') + len('</videos>')].replace('<videos>', '<home>').replace('</videos>', '</home>') + '</keymap>')


def sync(enabled=None):
    if enabled is None:
        enabled = ADDON.getSetting('normal_play') != 'false'
    existing = None
    if os.path.exists(PATH):
        with open(PATH, encoding='utf-8') as file:
            existing = file.read()
        if MARKER not in existing:
            raise RuntimeError('Existing zz-zidoo-bridge.xml is not bridge-owned; left unchanged')
    if enabled and existing != XML:
        os.makedirs(os.path.dirname(PATH), exist_ok=True)
        with open(PATH + '.tmp', 'w', encoding='utf-8') as file:
            file.write(XML)
        os.replace(PATH + '.tmp', PATH)
        xbmc.executebuiltin('Action(reloadkeymaps)')
    elif not enabled and existing is not None:
        os.remove(PATH)
        xbmc.executebuiltin('Action(reloadkeymaps)')
