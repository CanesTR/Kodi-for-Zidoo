import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'addon_0.7.22'))
from media_path import smb_mount, supported, same_result, display_path
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

    def test_credentials_not_displayed(self):
        self.assertEqual(display_path('smb://user:secret@nas/share/movie.mkv'), '<SMB credentials omitted>')


if __name__ == '__main__':
    unittest.main()
