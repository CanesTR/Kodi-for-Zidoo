# -*- coding: utf-8 -*-
import json
import os
import time
import uuid
import sqlite3
from contextlib import contextmanager
from urllib.parse import urlencode
import urllib.request
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
from bridge_logic import checked_resume
from media_path import supported, pinned_mount
from return_navigation import capture

ADDON = xbmcaddon.Addon('plugin.program.zidoo.bridge.diagnostic')
NAME = 'Kodi for Zidoo'
PROFILE = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
EXCHANGE = '/storage/emulated/0/Download/ZidooBridge/'
API = 'http://127.0.0.1:9529/ZidooVideoPlay/getPlayStatus'
PENDING = os.path.join(PROFILE, 'pending_session.json')
LOG = os.path.join(PROFILE, 'zidoo_bridge_diagnostic.log')
LATEST = os.path.join(PROFILE, 'latest_status.json')


def log(message):
    xbmc.log('[ZidooBridge] ' + message, xbmc.LOGINFO)
    with open(LOG, 'a', encoding='utf-8') as out:
        out.write(time.strftime('%Y-%m-%d %H:%M:%S ') + message + '\n')


def save(path, obj):
    with open(path + '.tmp', 'w', encoding='utf-8') as out:
        json.dump(obj, out, indent=2)
    os.replace(path + '.tmp', path)


def rpc(method, params):
    response = json.loads(xbmc.executeJSONRPC(json.dumps(
        {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params})))
    if 'error' in response:
        raise RuntimeError(method + ': ' + json.dumps(response['error']))
    return response['result']


def read_shared(path):
    if not xbmcvfs.exists(path):
        return None
    file = xbmcvfs.File(path)
    try:
        text = file.read()
    finally:
        file.close()
    if not text:
        return None  # The provider may expose the path before its write finishes.
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return None  # Retry an incomplete publication on the next poll.


MEDIA = {
    'movie': ('Movie', 'movieid', 'moviedetails'),
    'episode': ('Episode', 'episodeid', 'episodedetails'),
    'musicvideo': ('MusicVideo', 'musicvideoid', 'musicvideodetails'),
}


def media_identity(pending):
    kind = pending.get('media_type', 'movie')
    if kind not in MEDIA:
        raise ValueError('Unsupported library media type')
    itemid = pending.get('media_id', pending.get('movieid'))
    if type(itemid) is not int or itemid < 0:
        raise ValueError('Invalid library item ID')
    return kind, itemid


def detail(itemid, kind='movie'):
    suffix, idkey, resultkey = MEDIA[kind]
    return rpc('VideoLibrary.Get' + suffix + 'Details', {idkey: itemid,
               'properties': ['file', 'resume', 'playcount']})[resultkey]


def apply_result(pending, result, notify=True, on_return=None):
    try:
        resume, watched = checked_resume(pending, result)
    except ValueError as exc:
        save(LATEST, {'stage': 'rejected', 'pending': pending, 'native_result': result, 'error': str(exc)})
        if os.path.exists(PENDING):
            os.remove(PENDING)
        raise
    try:
        log('RETURN PROCESS ' + json.dumps({'session': pending.get('session'),
            'launch_pid': pending.get('kodi_pid'), 'return_pid': os.getpid(),
            'same_process': (pending.get('kodi_pid') == os.getpid()) if pending.get('kodi_pid') is not None else None,
            'window': xbmcgui.getCurrentWindowId(),
            'folder': xbmc.getInfoLabel('Container.FolderPath')}))
    except Exception:
        pass  # Diagnostics must never block a verified library update.
    kind, itemid = media_identity(pending)
    suffix, idkey, _ = MEDIA[kind]
    if on_return is not None:
        try:
            on_return(pending.get('return_context'))
        except Exception as exc:
            log('EARLY RETURN NAVIGATION ERROR ' + repr(exc))
    current = detail(itemid, kind)
    if current.get('file') != pending['path']:
        raise ValueError('Kodi library ID now points to another file')
    # Do not overwrite a bookmark someone changed while this session was pending.
    current_resume = current.get('resume', {})
    before = pending.get('before_resume', {})
    planned = pending.get('planned_resume')
    already = planned is not None and abs(float(current_resume.get('position', 0)) - resume['position']) <= 1.0 and abs(float(current_resume.get('total', 0)) - resume['total']) <= 1.0
    if watched:
        already = already and int(current.get('playcount', 0)) >= 1
    if not already:
        if abs(float(current_resume.get('position', 0)) - float(before.get('position', 0))) > 0.01 or abs(float(current_resume.get('total', 0)) - float(before.get('total', 0))) > 0.01:
            raise ValueError('Kodi resume changed during this session; no overwrite performed')
        params = {idkey: itemid, 'resume': resume}
        if watched:
            params['playcount'] = max(1, int(current.get('playcount', 0)))
        pending['planned_resume'] = resume
        pending['planned_watched'] = watched
        save(PENDING, pending)
        log('LIBRARY UPDATE ' + json.dumps(params))
        if rpc('VideoLibrary.Set' + suffix + 'Details', params) != 'OK':
            raise RuntimeError('Kodi did not acknowledge the resume update')
    actual = detail(itemid, kind)
    log('LIBRARY READBACK ' + json.dumps(actual))
    stored = actual.get('resume', {})
    if abs(float(stored.get('position', -1)) - resume['position']) > 1.0 or abs(float(stored.get('total', -1)) - resume['total']) > 1.0:
        raise RuntimeError('Kodi resume readback did not match; pending result retained')
    if watched and int(actual.get('playcount', 0)) < 1:
        raise RuntimeError('Kodi watched readback failed')
    payload = {'stage': 'verified', 'session': pending['session'], 'path': pending['path'],
               'external_uri': pending.get('external_uri'), 'return_context': pending.get('return_context'), 'media_type': kind, 'media_id': itemid, 'native_result': result, 'stored_movie': actual, 'watched_marked': watched}
    save(LATEST, payload)
    log('VERIFIED RESULT ' + json.dumps(payload))
    os.remove(PENDING)
    return payload


@contextmanager
def state_lock():
    os.makedirs(PROFILE, exist_ok=True)
    connection = sqlite3.connect(os.path.join(PROFILE, 'state_lock.sqlite'), timeout=5)
    try:
        connection.execute('BEGIN IMMEDIATE')
        yield
        connection.commit()
    finally:
        connection.close()


def load_pending():
    if not os.path.exists(PENDING):
        return None
    with open(PENDING, encoding='utf-8') as file:
        return json.load(file)


def process_pending(on_return=None):
    # Short cross-interpreter lock: the service and menu cannot apply twice.
    with state_lock():
        pending = load_pending()
        if pending is None:
            return None
        result = read_shared(EXCHANGE + 'bridge-result-' + pending['session'] + '.json')
        if result is None:
            return None
        try:
            payload = apply_result(pending, result, notify=False, on_return=on_return)
        except ValueError as exc:
            save(LATEST, {'stage': 'rejected', 'pending': pending, 'error': str(exc)})
            if os.path.exists(PENDING):
                os.remove(PENDING)
            raise
    return payload


def wait_result(pending):
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        process_pending()
        with state_lock():
            current = load_pending()
        if current is None or current['session'] != pending['session']:
            return
        if monitor.waitForAbort(2):
            return


def movies():
    found = []
    start = 0
    while True:
        response = rpc('VideoLibrary.GetMovies', {'properties': ['file', 'resume', 'playcount'],
                       'limits': {'start': start, 'end': start + 500},
                       'sort': {'method': 'label', 'order': 'ascending'}})
        chunk = response.get('movies', [])
        found.extend(m for m in chunk if supported(m.get('file', ''), ADDON.getSettingBool('experimental_smb')))
        end = response.get('limits', {}).get('end', start + len(chunk))
        if not chunk or end >= response.get('limits', {}).get('total', end):
            return found
        start = end


def preflight():
    if rpc('Player.GetActivePlayers', {}):
        raise RuntimeError('Stop playback in Kodi before starting Zidoo playback.')
    # A successful earlier report export proves the folder exists. Verify that Kodi can read it.
    _, files = xbmcvfs.listdir(EXCHANGE)
    reports = [n for n in files if n.startswith('zidoo-helper-report-') and n.endswith('.txt')]
    if not reports:
        raise RuntimeError('Kodi cannot see a helper report in Internal storage/Download/ZidooBridge. Export a report in the helper first.')
    file = xbmcvfs.File(EXCHANGE + sorted(reports)[-1])
    try:
        if not file.read():
            raise RuntimeError('Kodi cannot read the shared Downloads report')
    finally:
        file.close()
    with urllib.request.urlopen(API, timeout=3) as response:
        state = json.loads(response.read(262144).decode('utf-8'))
    if state.get('status') != 806:
        raise RuntimeError('The Zidoo player is already open. Close it before running this test.')


def main(movieid=None, kind='movie'):
    process_pending()
    with state_lock():
        pending = load_pending()
    if pending is not None:
        choice = xbmcgui.Dialog().select(NAME, ['Wait for the pending player result', 'Discard pending session'])
        if choice == 0:
            wait_result(pending)
            return
        if choice != 1:
            return
        with state_lock():
            current = load_pending()
            if current and current['session'] == pending['session']:
                os.remove(PENDING)
                log('Pending session discarded by user; no library update.')
    preflight()
    if movieid is None:
        items = movies()
        if not items:
            xbmcgui.Dialog().ok(NAME, 'No local /storage/... movies found in Kodi Movies library.')
            return
        index = xbmcgui.Dialog().select('Select a library movie for native playback',
                                       [m.get('label', '') + ' — ' + os.path.basename(m['file']) for m in items])
        if index < 0:
            return
        movieid = items[index]['movieid']
    movie = detail(movieid, kind)
    path = movie['file']
    if not supported(path, ADDON.getSettingBool('experimental_smb')):
        raise ValueError('Use a local /storage/ path or enable experimental SMB for a credential-free library file URL')
    expected_mount = pinned_mount(path, ADDON.getSetting('nas_hostname').strip(), ADDON.getSetting('nas_ipv4').strip()) if path.startswith('smb://') else ''
    return_context = capture()
    resume = movie.get('resume', {})
    settings = xbmcaddon.Addon('plugin.program.zidoo.bridge.diagnostic')
    native_resume = settings.getSettingBool('native_resume')
    log('RESUME MODE addon={} native={} raw={!r} source={}'.format(
        settings.getAddonInfo('version'), native_resume, settings.getSetting('native_resume'), __file__))
    start_ms = 0
    if not native_resume and float(resume.get('position', 0)) > 0:
        choice = xbmcgui.Dialog().select(NAME, ['Resume at {:.1f} seconds'.format(resume['position']), 'Play from beginning'])
        if choice < 0:
            log('RESUME PROMPT cancelled')
            return
        if choice == 0:
            start_ms = round(resume['position'] * 1000)
    if not 0 <= start_ms <= 2147483647:
        raise ValueError('Resume point exceeds native player range')
    pending = {'session': uuid.uuid4().hex, 'path': path, 'media_type': kind, 'media_id': movieid,
               'before_resume': resume, 'resume_ms': start_ms, 'native_resume': native_resume,
               'created': time.time(), 'return_context': return_context, 'expected_mount': expected_mount,
               'kodi_pid': os.getpid()}
    with state_lock():
        if load_pending() is not None:
            raise RuntimeError('Another bridge session is pending.')
        preflight()
        save(PENDING, pending)
        save(LATEST, {'stage': 'launch_requested', 'pending': pending})
    uri = 'zidoobridge://play?' + urlencode({'path': path, 'session': pending['session'], 'resume_ms': start_ms, 'native_resume': '1' if native_resume else '0', 'allow_smb': '1' if path.startswith('smb://') else '0', 'expected_mount': expected_mount})
    command = ('StartAndroidActivity(com.stormtracker.zidoobridge,android.intent.action.VIEW,'
               ',"{}",268435456,,,,com.stormtracker.zidoobridge.DiagnosticActivity)').format(uri)
    log('LAUNCH ' + json.dumps(pending))
    xbmc.executebuiltin(command)




def run(movieid=None, kind='movie'):
    xbmcvfs.mkdirs(PROFILE)
    try:
        main(movieid, kind)
    except Exception as exc:
        log('ERROR ' + repr(exc))
        xbmcgui.Dialog().ok(NAME, str(exc))


if __name__ == '__main__':
    run()
