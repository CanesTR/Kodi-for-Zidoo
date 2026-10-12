import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / 'addon_0.7.23'
sys.path.insert(0, str(ADDON))
from bridge_logic import checked_resume


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.pending = {'session': 'a' * 32, 'path': '/storage/752B-5666/Holiday Movies/A Biltmore Christmas.mp4', 'movieid': 7, 'before_resume': {'position': 0., 'total': 0.}}
        self.result = {'schema': 1, 'helper_version': '0.2.0', 'session': self.pending['session'], 'path': self.pending['path'], 'returned_path': self.pending['path'], 'status': 'completed', 'result_code': -1, 'position_ms': 67224, 'duration_ms': 5045642, 'end_by': 'user'}

    def test_helper_028_result_supported(self):
        resume, watched = checked_resume(self.pending, dict(self.result, helper_version='0.2.8'))
        self.assertEqual(resume['position'], 67.224)
        self.assertFalse(watched)

    def test_manual_helper_reset_clears_pending_without_library_write(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = self.load_bridge(directory)
            bridge.save(bridge.PENDING, self.pending)
            bridge.rpc = Mock()
            bridge.read_shared = Mock(return_value=dict(self.result, helper_version='0.2.8', status='error', result_code=0, error='Pending session reset by user'))
            with self.assertRaises(ValueError):
                bridge.process_pending()
            self.assertIsNone(bridge.load_pending())
            bridge.rpc.assert_not_called()

    def test_smb_final_result_updates_original_kodi_library_entry(self):
        from media_path import smb_mount
        path = 'smb://192.168.1.194/MEDIAS/FILMS/Test Movie/Film été.mkv'
        self.pending['path'] = path
        self.result.update(path=path, returned_path=smb_mount(path), helper_version='0.2.9')
        self.test_verified_update_and_retry_is_idempotent()

    def test_helper_023_result_supported(self):
        resume, watched = checked_resume(self.pending, dict(self.result, helper_version='0.2.3'))
        self.assertEqual(resume['position'], 67.224)
        self.assertFalse(watched)

    def test_native_resume_mode_skips_kodi_prompt_and_sets_uri(self):
        for native in (False, True):
            with tempfile.TemporaryDirectory() as directory:
                bridge = self.load_bridge(directory)
                bridge.ADDON.getSetting.side_effect = lambda key: ('True' if native else 'false') if key == 'native_resume' else 'false'
                bridge.ADDON.getSettingBool.return_value = native
                bridge.process_pending = Mock(return_value=None)
                bridge.preflight = Mock()
                bridge.capture = Mock(return_value=None)
                bridge.detail = Mock(return_value={'file': self.pending['path'], 'resume': {'position': 67.224, 'total': 5045.642}})
                dialog = Mock()
                dialog.select.return_value = 0
                sys.modules['xbmcgui'].Dialog.return_value = dialog
                sys.modules['xbmc'].executebuiltin = Mock()
                bridge.main(7)
                pending = bridge.load_pending()
                self.assertEqual(pending['native_resume'], native)
                self.assertEqual(pending['resume_ms'], 0 if native else 67224)
                self.assertEqual(dialog.select.call_count, 0 if native else 1)
                command = sys.modules['xbmc'].executebuiltin.call_args.args[0]
                self.assertIn('native_resume=' + ('1' if native else '0'), command)
                resume, watched = checked_resume(pending, dict(self.result, helper_version='0.2.4', session=pending['session']))
                self.assertEqual(resume['position'], 67.224)
                self.assertFalse(watched)

    def test_real_native_result_units(self):
        resume, watched = checked_resume(self.pending, self.result)
        self.assertEqual(resume, {'position': 67.224, 'total': 5045.642})
        self.assertFalse(watched)

    def test_reject_mismatched_or_failed_results(self):
        for key, value in [('session', 'b' * 32), ('path', '/storage/other.mp4'), ('returned_path', '/storage/other.mp4'), ('status', 'error'), ('result_code', 0), ('end_by', ''), ('position_ms', -1), ('position_ms', 9999999), ('duration_ms', 0), ('position_ms', True), ('helper_version', '0.1.1')]:
            with self.subTest(key=key, value=value):
                result = dict(self.result, **{key: value})
                with self.assertRaises(ValueError):
                    checked_resume(self.pending, result)

    def test_watched_is_automatic_at_90_percent(self):
        for setting in (None, False, True):
            pending = dict(self.pending)
            if setting is not None:
                pending['mark_watched'] = setting
            for position in (89999, 90000, 100000):
                resume, watched = checked_resume(pending, dict(self.result, position_ms=position, duration_ms=100000))
                self.assertEqual(watched, position >= 90000)
                self.assertEqual(resume['position'], 0. if watched else position / 1000.)
                self.assertEqual(resume['total'], 0. if watched else 100.)

    def load_bridge(self, directory):
        for name in ['xbmc', 'xbmcaddon', 'xbmcgui', 'xbmcvfs']:
            sys.modules[name] = types.ModuleType(name)
        addon = Mock()
        addon.getAddonInfo.side_effect = lambda key: directory if key == 'profile' else 'test'
        sys.modules['xbmcaddon'].Addon = Mock(return_value=addon)
        sys.modules['xbmcvfs'].translatePath = lambda p: p
        sys.modules['xbmcgui'].Dialog = Mock(return_value=Mock())
        spec = importlib.util.spec_from_file_location('bridge_under_test', ADDON / 'default.py')
        bridge = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bridge)
        sys.modules['xbmcaddon'].Addon.assert_called_once_with('plugin.program.zidoo.bridge.diagnostic')
        bridge.log = Mock()
        return bridge

    def test_verified_update_and_retry_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = self.load_bridge(directory)
            db = {'movieid': 7, 'file': self.pending['path'], 'resume': {'position': 0., 'total': 0.}, 'playcount': 0}
            writes = []
            def rpc(method, params):
                if method.endswith('GetMovieDetails'):
                    return {'moviedetails': json.loads(json.dumps(db))}
                writes.append(params)
                db['resume'] = {k: float(int(v)) for k, v in params['resume'].items()}
                return 'OK'
            bridge.rpc = rpc
            pending = dict(self.pending)
            bridge.save(bridge.PENDING, pending)
            bridge.apply_result(pending, self.result)
            self.assertEqual(len(writes), 1)
            self.assertEqual(db['resume']['position'], 67.0)
            self.assertNotIn('playcount', writes[0])
            self.assertFalse(Path(bridge.PENDING).exists())
            # Simulate a crash after the write but before pending deletion.
            bridge.save(bridge.PENDING, pending)
            bridge.apply_result(pending, self.result)
            self.assertEqual(len(writes), 1)

    def test_changed_library_path_or_bookmark_never_written(self):
        for change in [{'file': '/storage/different.mp4'}, {'resume': {'position': 300., 'total': 5045.642}}]:
            with tempfile.TemporaryDirectory() as directory:
                bridge = self.load_bridge(directory)
                db = {'file': self.pending['path'], 'resume': {'position': 0., 'total': 0.}, **change}
                bridge.rpc = Mock(return_value={'moviedetails': db})
                with self.assertRaises(ValueError):
                    bridge.apply_result(dict(self.pending), self.result)
                self.assertEqual(bridge.rpc.call_count, 1)

    def test_shared_file_publication_is_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = self.load_bridge(directory)
            vfs = sys.modules['xbmcvfs']
            vfs.exists = lambda _: True
            file = Mock()
            vfs.File = lambda _: file
            file.read.side_effect = ['', '{"session":', '{"schema":1}']
            self.assertIsNone(bridge.read_shared('session.json'))
            self.assertIsNone(bridge.read_shared('session.json'))
            self.assertEqual(bridge.read_shared('session.json'), {'schema': 1})
            self.assertEqual(file.close.call_count, 3)

    def test_new_helper_result_compatible(self):
        resume, watched = checked_resume(self.pending, dict(self.result, helper_version='0.2.1'))
        self.assertEqual(resume['position'], 67.224)
        self.assertFalse(watched)

    def test_watched_clears_both_resume_values_and_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = self.load_bridge(directory)
            db = {'movieid': 7, 'file': self.pending['path'], 'resume': {'position': 0., 'total': 0.}, 'playcount': 0}
            writes = []
            def rpc(method, params):
                if method.endswith('GetMovieDetails'):
                    return {'moviedetails': json.loads(json.dumps(db))}
                writes.append(params)
                db['resume'] = {'position': 0., 'total': 0.}
                db['playcount'] = params['playcount']
                return 'OK'
            bridge.rpc = rpc
            pending = dict(self.pending, mark_watched=True)
            result = dict(self.result, position_ms=6008246, duration_ms=6072554)
            bridge.save(bridge.PENDING, pending)
            bridge.apply_result(pending, result)
            self.assertEqual(writes[0]['resume'], {'position': 0., 'total': 0.})
            self.assertEqual(db['playcount'], 1)
            self.assertFalse(Path(bridge.PENDING).exists())
            # Recover an old plan with a retained total after the successful write.
            pending['planned_resume']['total'] = 6072.554
            bridge.save(bridge.PENDING, pending)
            bridge.apply_result(pending, result)
            self.assertEqual(len(writes), 1)

    def test_bad_native_result_makes_no_rpc_call(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = self.load_bridge(directory)
            bridge.rpc = Mock()
            with self.assertRaises(ValueError):
                bridge.apply_result(self.pending, dict(self.result, session='bad'))
            bridge.rpc.assert_not_called()

    def test_background_workers_apply_once(self):
        import concurrent.futures
        import time
        with tempfile.TemporaryDirectory() as directory:
            bridge = self.load_bridge(directory)
            db = {'movieid': 7, 'file': self.pending['path'], 'resume': {'position': 0., 'total': 0.}, 'playcount': 0}
            writes = []
            def rpc(method, params):
                if method.endswith('GetMovieDetails'):
                    return {'moviedetails': json.loads(json.dumps(db))}
                time.sleep(0.03)
                writes.append(params)
                db['resume'] = params['resume']
                return 'OK'
            bridge.rpc = rpc
            bridge.read_shared = lambda _: self.result
            bridge.save(bridge.PENDING, self.pending)
            with concurrent.futures.ThreadPoolExecutor(2) as workers:
                outcomes = list(workers.map(lambda _: bridge.process_pending(), range(2)))
            self.assertEqual(len(writes), 1)
            self.assertEqual(sum(x is not None for x in outcomes), 1)
            self.assertFalse(Path(bridge.PENDING).exists())

    def test_background_failure_retains_for_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = self.load_bridge(directory)
            bridge.read_shared = lambda _: self.result
            bridge.rpc = Mock(side_effect=RuntimeError('RPC unavailable'))
            bridge.save(bridge.PENDING, self.pending)
            with self.assertRaises(RuntimeError):
                bridge.process_pending()
            self.assertTrue(Path(bridge.PENDING).exists())
            bridge.rpc = Mock(return_value={'moviedetails': {'file': self.pending['path'], 'resume': {'position': 99., 'total': 100.}}})
            with self.assertRaises(ValueError):
                bridge.process_pending()
            self.assertFalse(Path(bridge.PENDING).exists())
            self.assertEqual(json.loads(Path(bridge.LATEST).read_text())['stage'], 'rejected')

    def test_preflight_blocks_kodi_playback(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = self.load_bridge(directory)
            bridge.rpc = Mock(return_value=[{'playerid': 1, 'type': 'video'}])
            with self.assertRaisesRegex(RuntimeError, 'Stop playback'):
                bridge.preflight()

    def test_episode_and_musicvideo_resume_use_correct_library(self):
        for kind, suffix, idkey, resultkey in [('episode', 'Episode', 'episodeid', 'episodedetails'), ('musicvideo', 'MusicVideo', 'musicvideoid', 'musicvideodetails')]:
            for watched in (False, True):
                with self.subTest(kind=kind, watched=watched), tempfile.TemporaryDirectory() as directory:
                    bridge = self.load_bridge(directory)
                    pending = dict(self.pending, media_type=kind, media_id=42, mark_watched=watched)
                    pending.pop('movieid')
                    result = dict(self.result, position_ms=95000, duration_ms=100000) if watched else self.result
                    db = {'file': pending['path'], idkey: 42, 'resume': {'position': 0., 'total': 0.}, 'playcount': 0}
                    writes = []
                    def rpc(method, params):
                        self.assertEqual(params[idkey], 42)
                        self.assertNotIn('movieid', params)
                        if method == 'VideoLibrary.Get' + suffix + 'Details':
                            return {resultkey: json.loads(json.dumps(db))}
                        self.assertEqual(method, 'VideoLibrary.Set' + suffix + 'Details')
                        writes.append(params)
                        db['resume'] = params['resume']
                        db['playcount'] = params.get('playcount', 0)
                        return 'OK'
                    bridge.rpc = rpc
                    bridge.save(bridge.PENDING, pending)
                    payload = bridge.apply_result(pending, result)
                    self.assertEqual(len(writes), 1)
                    self.assertEqual(payload['media_type'], kind)
                    self.assertEqual(payload['watched_marked'], watched)
                    self.assertEqual(db['resume']['position'], 0. if watched else 67.224)

    def test_normal_select_routes_only_local_library_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = self.load_bridge(directory)
            sys.modules['default'] = bridge
            spec = importlib.util.spec_from_file_location('normal_select', ADDON / 'normal_select.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for kind in ['movie', 'episode', 'musicvideo']:
                self.assertEqual(module.route(kind, '28', '/storage/drive/clip.mkv'), (28, kind))
            for kind, itemid, path in [('tvshow', '28', '/storage/drive'), ('movie', '', '/storage/clip'), ('movie', '-1', '/storage/clip'), ('movie', '1', 'plugin://video'), ('', '', '')]:
                self.assertIsNone(module.route(kind, itemid, path))
            self.assertIsNone(module.route('movie', '1', '/storage/clip', enabled=False))

    def test_keymap_install_disable_and_protect_other_file(self):
        import xml.etree.ElementTree as ET
        with tempfile.TemporaryDirectory() as directory:
            bridge = self.load_bridge(directory)
            sys.modules['default'] = bridge
            sys.modules['xbmc'].executebuiltin = Mock()
            spec = importlib.util.spec_from_file_location('normal_keymap', ADDON / 'normal_keymap.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.PATH = str(Path(directory) / 'keymaps' / 'zz-zidoo-bridge.xml')
            module.sync(True)
            root = ET.parse(module.PATH).getroot()
            self.assertIsNotNone(root.find('videos/remote/select'))
            self.assertIsNone(root.find('global'))
            self.assertIsNotNone(root.find('home/remote/select'))
            for window in ('videos', 'home'):
                for device, key in (('keyboard', 'return'), ('keyboard', 'enter'), ('remote', 'select')):
                    buttons = root.findall(window + '/' + device + '/' + key)
                    short = [b for b in buttons if b.get('mod') is None]
                    long = [b for b in buttons if b.get('mod') == 'longpress']
                    self.assertEqual(len(short), 1)
                    self.assertTrue(short[0].text.startswith('RunScript('))
                    self.assertEqual(len(long), 1)
                    self.assertEqual(long[0].text, 'ContextMenu')
            module.sync(True)
            self.assertEqual(sys.modules['xbmc'].executebuiltin.call_count, 1)
            module.sync(False)
            self.assertFalse(Path(module.PATH).exists())
            Path(module.PATH).write_text('<keymap>user mapping</keymap>')
            with self.assertRaises(RuntimeError): module.sync(True)
            self.assertEqual(Path(module.PATH).read_text(), '<keymap>user mapping</keymap>')


if __name__ == '__main__':
    unittest.main()
