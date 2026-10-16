import com.stormtracker.zidoobridge.MediaPath;

public class MediaPathTest {
    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
    public static void main(String[] args) throws Exception {
        String path = "smb://192.168.1.194/MEDIAS/FILMS/MKV/#Chef (2014) (mkv)/#Chef (2014) h264-1080p AC3-6ch.mkv";
        String mount = "/mnt/smb/192.168.1.194#MEDIAS/FILMS/MKV/#Chef (2014) (mkv)/#Chef (2014) h264-1080p AC3-6ch.mkv";
        check(MediaPath.smbMount(path).equals(mount), "Exact tester path");
        check(MediaPath.smbMount(path.replace("#", "%23")).equals(mount), "Encoded hash");
        check(MediaPath.sameResult(path, mount), "Mounted result");
        check(MediaPath.sameResult(path, path.replace("#", "%23")), "SMB result");
        check(!MediaPath.sameResult(path, mount.replace("/#Chef", "/Chef")), "Wrong file rejected");
        check(!MediaPath.sameResult(path, mount.replace("1.194#", "1.195#")), "Wrong host rejected");
        String alias = path.replace("192.168.1.194", "NAS");
        check(MediaPath.validPinnedMount(alias, mount), "Pinned alias with hashes");
        check(MediaPath.sameResult(alias, mount, mount), "Pinned result with hashes");
        check(!MediaPath.validPinnedMount(alias, mount.replace("/#Chef", "/Chef")), "Wrong pinned file rejected");
        check(MediaPath.smbMount("smb://NAS/Public/a%2523b.mkv").equals("/mnt/smb/NAS#Public/a%23b.mkv"), "Decode once");
        check(MediaPath.smbMount("smb://NAS/Public/a#b+é.mkv").equals("/mnt/smb/NAS#Public/a#b+é.mkv"), "Unicode and plus preserved");
        for (String bad : new String[]{"smb://NA#S/Public/a.mkv", "smb://NAS/#Public/a.mkv",
                "smb://user:secret@NAS/Public/a#b.mkv", "smb://NAS:445/Public/a#b.mkv",
                "smb://NAS/Public/a#b.mkv?x=1", "smb://NAS/Public/#a/%2e%2e/b.mkv",
                "smb://NAS/Public/#a/b%2fc.mkv", "smb://NAS/Public/a%ZZ.mkv"}) {
            boolean rejected = false;
            try { MediaPath.smbMount(bad); } catch (Exception expected) { rejected = true; }
            check(rejected, "Unsafe path rejected: " + bad);
        }
        check(MediaPath.sameResult("/storage/drive/#Movie.mkv", "/storage/drive/#Movie.mkv"), "Local unchanged");
        System.out.println("Java MediaPath checks passed");
    }
}
