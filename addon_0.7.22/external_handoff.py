"""Opt-in Python external-player handoff; rules match only session URIs."""
import os
import shutil
import xml.etree.ElementTree as ET
import xbmc
import xbmcgui
import xbmcvfs
from default import ADDON, log, rpc

PLAYER_NAME = 'Kodi for Zidoo Bridge Test'
PATH = xbmcvfs.translatePath('special://profile/playercorefactory.xml')
OWNER = 'zidoo-bridge-external-test'


def sync():
    enabled = False  # Public release: remove legacy test configuration only.
    exists = os.path.exists(PATH)
    if exists:
        tree = ET.parse(PATH, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
        root = tree.getroot()
        if root.tag != 'playercorefactory':
            raise ValueError('Unexpected playercorefactory.xml; left unchanged')
    else:
        if not enabled:
            return
        root = ET.Element('playercorefactory')
        tree = ET.ElementTree(root)
    players = root.find('players')
    entry = None if players is None else next((p for p in players.findall('player') if p.get('name') == PLAYER_NAME), None)
    if entry is not None and entry.get('bridge_owner') != OWNER:
        raise ValueError('External player name already in use; left unchanged')
    owned_rules = [node for node in root.findall('rules') if node.get('bridge_owner') == OWNER]
    valid_rule = len(owned_rules) == 1 and len(owned_rules[0]) == 1 and owned_rules[0][0].get('protocols') == '^zidoobridge$' and owned_rules[0][0].get('player') == PLAYER_NAME
    if enabled and entry is not None and valid_rule:
        return
    if not enabled and entry is None and not owned_rules:
        return
    for node in owned_rules:
        root.remove(node)
    if enabled:
        if players is None:
            players = ET.SubElement(root, 'players')
        if entry is None:
            entry = ET.SubElement(players, 'player', {'name': PLAYER_NAME, 'type': 'ExternalPlayer',
                                  'audio': 'false', 'video': 'true', 'bridge_owner': OWNER})
            for key, value in [('filename', 'com.stormtracker.zidoobridge'), ('hidexbmc', 'true'),
                               ('playcountminimumtime', '2147483647')]:
                ET.SubElement(entry, key).text = value
        rules = ET.Element('rules', {'action':'prepend', 'bridge_owner':OWNER})
        ET.SubElement(rules, 'rule', {'protocols':'^zidoobridge$', 'player':PLAYER_NAME})
        # Last prepend block puts this URI-only rule first in the runtime list.
        root.append(rules)
    elif entry is not None:
        players.remove(entry)
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    if exists and not os.path.exists(PATH + '.before-zidoo-external-test'):
        shutil.copy2(PATH, PATH + '.before-zidoo-external-test')
    tree.write(PATH + '.tmp', encoding='utf-8', xml_declaration=True)
    os.replace(PATH + '.tmp', PATH)
    log('PYTHON EXTERNAL CONFIG ' + ('installed' if enabled else 'removed') + '; restart Kodi to apply')


def rules_configured():
    if not os.path.exists(PATH):
        return False
    root = ET.parse(PATH).getroot()
    return any(node.get('bridge_owner') == OWNER and
               any(rule.get('protocols') == '^zidoobridge$' and rule.get('player') == PLAYER_NAME
                   for rule in node.findall('rule')) for node in root.findall('rules'))


def configured():
    # media=video excludes video-only players on this Kodi build.
    players = rpc('Player.GetPlayers', {'media':'all'})
    present = any(p.get('name') == PLAYER_NAME and p.get('type') == 'external'
                  and p.get('playsvideo') is True for p in players)
    if not present:
        log('EXTERNAL PLAYER registry ' + repr(players))
    return present


def launch(uri):
    if not uri.startswith('zidoobridge://play?'):
        raise ValueError('Unexpected external session URI')
    item = xbmcgui.ListItem(label='Kodi for Zidoo', path=uri)
    item.setMimeType('video/mp4')
    item.setContentLookup(False)
    item.setProperty('IsPlayable', 'true')
    # No movie DBID: Kodi's generic external bookkeeping applies to this URI,
    # while the verified bridge callback updates the real library item.
    xbmc.Player().play(uri, item, windowed=True)


def close_session(payload):
    uri = payload.get('external_uri')
    if not uri:
        return
    try:
        player = xbmc.Player()
        if player.isExternalPlayer() and player.getPlayingFile() == uri:
            player.stop()
            log('EXTERNAL HANDOFF session closed')
    except Exception as exc:
        log('EXTERNAL HANDOFF close failed ' + repr(exc))
