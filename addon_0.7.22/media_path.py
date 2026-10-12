"""Strict identities for the SMB-to-mount mapping observed on Zidoo."""
import re
from urllib.parse import urlsplit, unquote


def smb_mount(path):
    if not isinstance(path, str) or not path.startswith('smb://'):
        raise ValueError('A credential-free SMB file URL is required')
    uri = urlsplit(path)
    if not re.fullmatch(r'[A-Za-z0-9._-]+', uri.netloc or '') or uri.query or uri.fragment:
        raise ValueError('SMB credentials, ports, queries and fragments are not supported')
    if re.search(r'%(?![0-9A-Fa-f]{2})', uri.path):
        raise ValueError('Malformed SMB URL escape')
    raw = uri.path.split('/')
    if len(raw) < 3 or raw[0] != '':
        raise ValueError('A complete SMB file path is required')
    parts = [unquote(p, encoding='utf-8', errors='strict') for p in raw[1:]]
    if any(not p or p in ('.', '..') or any(c in p for c in '/\\\x00') for p in parts):
        raise ValueError('Invalid SMB path segment')
    if '#' in parts[0]:
        raise ValueError('Unsupported SMB share name')
    if not re.fullmatch(r'.+\.(mkv|mp4|m4v|avi|mov|ts|m2ts|mts|mpg|mpeg|iso|vob|wmv|webm)', parts[-1], re.IGNORECASE):
        raise ValueError('A complete supported video filename is required')
    return '/mnt/smb/' + uri.netloc + '#' + '/'.join(parts)


def supported(path, smb_enabled=False):
    if not isinstance(path, str):
        return False
    if path.startswith('/storage/'):
        return '\x00' not in path and '/../' not in path
    if smb_enabled:
        try:
            smb_mount(path)
            return True
        except (ValueError, UnicodeError):
            pass
    return False


def same_result(selected, returned):
    if selected.startswith('smb://'):
        try:
            expected = smb_mount(selected)
            actual = smb_mount(returned) if isinstance(returned, str) and returned.startswith('smb://') else returned
            return expected == actual
        except (ValueError, UnicodeError):
            return False
    return selected == returned


def display_path(path):
    if isinstance(path, str) and path.startswith('smb://'):
        try:
            if not re.fullmatch(r'[A-Za-z0-9._-]+', urlsplit(path).netloc or ''):
                return '<SMB credentials omitted>'
        except ValueError:
            return '<invalid SMB URL>'
    return path
