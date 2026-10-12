import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'addon_0.7.23'))
from media_path import smb_mount, supported, same_result, display_path, pinned_mount, valid_pinned_mount
from bridge_logic import checked_resume


class SmbTests(unittest.TestCase):
    path = 'smb://192.168.1.194/MEDIAS/FILMS/MKV UHD REMUX/Test Movie (2025)/Film été+1.mkv'
    mount = '/mnt/smb/192.168.1.194#MEDIAS/FILMS/MKV UHD REMUX/Test Movie (2025)/Film été+1.mkv'

    def test_observed_mount_mapping(self):
        self.assertEqual(smb_mount(self.path), self.mount)
        self.assertTrue(same_result(self.path, self.mount))

    def test_encoded_unicode_and_literal_plus(self):
        encoded = self.path.replace(' ', '%20').replace('é', '%C3%A9')
        self.assertEqual(smb_mount(encoded), self.mount)
        self.assertTrue(same_result(self.path, encoded))

    def test_opt_in_and_local_regression(self):
        self.assertFalse(supported(self.path))
        self.assertTrue(supported(self.path, True))
        self.assertTrue(supported('/storage/drive/Movie.mkv'))
        self.assertFalse(same_result('/storage/drive/Movie.mkv', '/storage/other/Movie.mkv'))

    def test_different_host_share_folder_filename_and_case_rejected(self):
        for wrong in [self.mount.replace('1.194', '1.195'), self.mount.replace('#MEDIAS', '#OTHER'),
                      self.mount.replace('/FILMS/', '/SERIES/'), self.mount.replace('Film été+1', 'Other'),
                      self.mount.replace('#MEDIAS', '#medias'), self.mount + '.bak']:
            self.assertFalse(same_result(self.path, wrong))

    def test_unsafe_or_ambiguous_urls_rejected(self):
        for path in ['smb://user:secret@nas/share/movie.mkv', 'smb://nas:445/share/movie.mkv',
                     'smb://nas/share', 'smb://nas/share/', 'smb://nas/share/../movie.mkv',
                     'smb://nas/share/%2e%2e/movie.mkv', 'smb://nas/share/a%2Fb.mkv',
                     'smb://nas/share/a%5Cb.mkv', 'smb://nas/share/a%00.mkv',
                     'smb://nas/share/movie%ZZ.mkv', 'smb://nas/share/movie.nfo', 'smb://nas/share/movie.mkv?x=1', 'smb://nas/share/movie.mkv#fragment']:
            self.assertFalse(supported(path, True), path)

    def test_network_result_retains_selected_library_identity(self):
        pending = {'session': 'a' * 32, 'path': self.path}
        result = {'schema': 1, 'helper_version': '0.2.9', 'session': pending['session'],
                  'path': self.path, 'returned_path': self.mount, 'status': 'completed',
                  'result_code': -1, 'position_ms': 340646, 'duration_ms': 6003360, 'end_by': 'user'}
        resume, watched = checked_resume(pending, result)
        self.assertEqual(resume['position'], 340.646)
        self.assertFalse(watched)
        resume, watched = checked_resume(pending, dict(result, position_ms=5403024))
        self.assertTrue(watched)
        self.assertEqual(resume['position'], 0)
        for key, value in [('session', 'b' * 32), ('path', self.mount), ('returned_path', self.mount + '.bak')]:
            with self.assertRaises(ValueError): checked_resume(pending, dict(result, **{key: value}))

    def test_configured_alias_is_pinned_for_result_validation(self):
        path = 'smb://WDMYCLOUD1/Public/Test Folder/Welcome 2.mp4'
        expected = '/mnt/smb/192.168.1.17#Public/Test Folder/Welcome 2.mp4'
        self.assertEqual(pinned_mount(path, 'wdmycloud1', '192.168.1.17'), expected)
        self.assertTrue(valid_pinned_mount(path, expected))
        pending = {'session': 'a'*32, 'path': path, 'expected_mount': expected}
        result = {'schema':1, 'helper_version':'0.2.10', 'session':'a'*32, 'path':path,
                  'expected_mount':expected, 'returned_path':expected, 'status':'completed',
                  'result_code':-1, 'end_by':'user', 'position_ms':5732, 'duration_ms':22260}
        resume, watched = checked_resume(pending, result)
        self.assertEqual(resume['position'], 5.732)
        self.assertFalse(watched)
        for key, value in [('returned_path', expected.replace('1.17','1.18')),
                           ('returned_path', expected.replace('#Public','#Other')),
                           ('returned_path', expected.replace('Welcome 2','Welcome 3')),
                           ('expected_mount', expected.replace('1.17','1.18'))]:
            with self.assertRaises(ValueError): checked_resume(pending, dict(result, **{key:value}))
        with self.assertRaises(ValueError): checked_resume(dict(pending, expected_mount=expected.replace('#Public','#Other')), result)

    def test_alias_does_not_apply_to_other_servers(self):
        self.assertEqual(pinned_mount(self.path, 'WDMYCLOUD1', '192.168.1.17'), self.mount)
        self.assertEqual(pinned_mount(self.path), self.mount)

    def test_incomplete_or_invalid_alias_rejected(self):
        for host, ip in [('WDMYCLOUD1',''), ('','192.168.1.17'), ('WDMYCLOUD1','192.168.1.999'),
                         ('WDMYCLOUD1','192.168.01.17'), ('user@host','192.168.1.17')]:
            with self.assertRaises(ValueError): pinned_mount(self.path, host, ip)
        self.assertFalse(valid_pinned_mount(self.path, self.mount.replace('192.168.1.194','not-a-mapped-host')))

    def test_credentials_not_displayed(self):
        self.assertEqual(display_path('smb://user:secret@nas/share/movie.mkv'), '<SMB credentials omitted>')


if __name__ == '__main__':
    unittest.main()
