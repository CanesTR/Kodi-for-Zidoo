package com.stormtracker.zidoobridge;

import java.net.URI;
import java.net.URLDecoder;

/** Exact host/share/file identity; never compare only the filename. */
public final class MediaPath {
    private MediaPath() {}

    public static String smbMount(String path) throws Exception {
        if (path == null || !path.startsWith("smb://")) throw new IllegalArgumentException("SMB file URL required");
        URI uri = new URI(path.replace(" ", "%20"));
        String host = uri.getRawAuthority();
        if (host == null || !host.matches("[A-Za-z0-9._-]+") || uri.getRawQuery() != null || uri.getRawFragment() != null)
            throw new IllegalArgumentException("SMB credentials, ports, query or fragment not supported");
        String rawPath = uri.getRawPath();
        if (rawPath == null) throw new IllegalArgumentException("Missing SMB file path");
        String[] raw = rawPath.split("/", -1);
        if (raw.length < 3 || !raw[0].isEmpty()) throw new IllegalArgumentException("Complete SMB file path required");
        StringBuilder result = new StringBuilder("/mnt/smb/").append(host).append('#');
        for (int i = 1; i < raw.length; i++) {
            String segment = URLDecoder.decode(raw[i].replace("+", "%2B"), "UTF-8");
            if (segment.isEmpty() || segment.equals(".") || segment.equals("..")
                    || segment.indexOf('/') >= 0 || segment.indexOf('\\') >= 0 || segment.indexOf('\0') >= 0
                    || (i == 1 && segment.indexOf('#') >= 0))
                throw new IllegalArgumentException("Invalid SMB path segment");
            if (i > 1) result.append('/');
            result.append(segment);
        }
        return result.toString();
    }

    public static boolean sameResult(String selected, String returned) {
        if (selected == null || returned == null) return false;
        if (!selected.startsWith("smb://")) return selected.equals(returned);
        try {
            String expected = smbMount(selected);
            String actual = returned.startsWith("smb://") ? smbMount(returned) : returned;
            return expected.equals(actual);
        } catch (Exception invalid) { return false; }
    }
}
