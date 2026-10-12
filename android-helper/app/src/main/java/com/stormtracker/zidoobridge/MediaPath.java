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

    public static boolean validPinnedMount(String selected, String expected) {
        try {
            String original = smbMount(selected);
            String prefix = "/mnt/smb/";
            if (expected == null || !expected.startsWith(prefix)) return false;
            int separator = expected.indexOf('#', prefix.length());
            if (separator < 0) return false;
            String host = expected.substring(prefix.length(), separator);
            String originalHost = original.substring(prefix.length(), original.indexOf('#'));
            if (!expected.substring(separator).equals(original.substring(original.indexOf('#')))) return false;
            if (host.equals(originalHost)) return true;
            String[] octets = host.split("\\.", -1);
            if (octets.length != 4) return false;
            for (String octet : octets) {
                if (!octet.matches("0|[1-9][0-9]{0,2}") || Integer.parseInt(octet) > 255) return false;
            }
            return true;
        } catch (Exception invalid) { return false; }
    }

    public static boolean sameResult(String selected, String returned, String expected) {
        if (expected == null || expected.isEmpty()) return sameResult(selected, returned);
        if (!validPinnedMount(selected, expected)) return false;
        return sameResult(selected, returned) || expected.equals(returned);
    }
}
