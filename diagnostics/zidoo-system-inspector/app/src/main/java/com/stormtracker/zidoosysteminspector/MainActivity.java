package com.stormtracker.zidoosysteminspector;

import android.app.Activity;
import android.app.ActivityManager;
import android.content.ContentValues;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.File;
import java.io.FileInputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

public class MainActivity extends Activity {
    private static final String FORCE_STOP = "android.permission.FORCE_STOP_PACKAGES";
    private TextView status;
    private Button save;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(36, 28, 36, 28);
        TextView title = new TextView(this);
        title.setTextSize(24);
        title.setText("Zidoo System Inspector 0.1.0");
        layout.addView(title);
        TextView explanation = new TextView(this);
        explanation.setText("Save a report and copies of selected installed system APKs for code inspection. "
            + "Includes system apps granted permission to force-stop apps, plus Zidoo's player and launcher. "
            + "Also records any process names Android makes visible. PID identification is not guaranteed. "
            + "No settings are changed. No app data, media paths, passwords or playback history are collected. "
            + "The ZIP may be large; upload it privately for analysis rather than publishing vendor APKs.");
        explanation.setTextSize(18);
        layout.addView(explanation);
        save = new Button(this);
        save.setText("Save analysis ZIP to Downloads");
        layout.addView(save);
        status = new TextView(this);
        status.setTextSize(18);
        status.setText("Ready. No ADB or developer options required.");
        layout.addView(status);
        setContentView(layout);
        save.requestFocus();
        save.setOnClickListener(v -> {
            save.setEnabled(false);
            status.setText("Collecting system information and copying APKs...");
            new Thread(() -> {
                try {
                    String filename = export();
                    runOnUiThread(() -> { status.setText("Saved: Internal storage/Download/ZidooSystemInspector/" + filename);
                        save.setEnabled(true); });
                } catch (Exception e) {
                    runOnUiThread(() -> { status.setText("Could not save: " + e.getClass().getSimpleName() + ": " + e.getMessage());
                        save.setEnabled(true); });
                }
            }, "system-inspection-export").start();
        });
    }

    private String export() throws Exception {
        PackageManager pm = getPackageManager();
        JSONObject report = new JSONObject();
        report.put("schema", 1);
        report.put("timestamp_ms", System.currentTimeMillis());
        report.put("model", Build.MODEL);
        report.put("manufacturer", Build.MANUFACTURER);
        report.put("sdk", Build.VERSION.SDK_INT);
        report.put("firmware_fingerprint", Build.FINGERPRINT);
        report.put("process_visibility_note", "Android may expose only this application's processes; missing PIDs are inconclusive.");
        JSONArray processes = new JSONArray();
        List<ActivityManager.RunningAppProcessInfo> visible = ((ActivityManager)getSystemService(ACTIVITY_SERVICE)).getRunningAppProcesses();
        if (visible != null) for (ActivityManager.RunningAppProcessInfo p : visible) {
            JSONObject item = new JSONObject();
            item.put("pid", p.pid); item.put("uid", p.uid); item.put("process", p.processName);
            processes.put(item);
        }
        report.put("visible_processes", processes);
        List<PackageInfo> packages = pm.getInstalledPackages(PackageManager.GET_PERMISSIONS);
        Collections.sort(packages, (a, b) -> a.packageName.compareTo(b.packageName));
        JSONArray selected = new JSONArray();
        List<PackageInfo> apkPackages = new ArrayList<>();
        for (PackageInfo p : packages) {
            boolean system = (p.applicationInfo.flags & (ApplicationInfo.FLAG_SYSTEM | ApplicationInfo.FLAG_UPDATED_SYSTEM_APP)) != 0;
            boolean canStop = pm.checkPermission(FORCE_STOP, p.packageName) == PackageManager.PERMISSION_GRANTED;
            String name = p.packageName;
            boolean playbackOrLauncher = name.equals("com.zidoo.player") || name.equals("com.android.gallery3d")
                || (system && (name.toLowerCase(java.util.Locale.ROOT).contains("zidoo")
                    || name.toLowerCase(java.util.Locale.ROOT).contains("launcher")));
            if (!(system && canStop) && !playbackOrLauncher) continue;
            JSONObject item = new JSONObject();
            item.put("package", name); item.put("label", pm.getApplicationLabel(p.applicationInfo).toString());
            item.put("version", p.versionName); item.put("uid", p.applicationInfo.uid);
            item.put("system", system); item.put("force_stop_permission_granted", canStop);
            item.put("apk_path", p.applicationInfo.sourceDir);
            JSONArray permissions = new JSONArray();
            if (p.requestedPermissions != null) for (String permission : p.requestedPermissions) permissions.put(permission);
            item.put("requested_permissions", permissions);
            selected.put(item);
            // Framework package is a resource APK, not a candidate app implementation.
            if (!name.equals("android")) apkPackages.add(p);
        }
        report.put("selected_packages", selected);
        String filename = "zidoo-system-analysis-" + System.currentTimeMillis() + ".zip";
        ContentValues values = new ContentValues();
        values.put(MediaStore.Downloads.DISPLAY_NAME, filename);
        values.put(MediaStore.Downloads.MIME_TYPE, "application/zip");
        values.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ZidooSystemInspector");
        values.put(MediaStore.Downloads.IS_PENDING, 1);
        Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
        if (uri == null) throw new java.io.IOException("Downloads could not create the file");
        try {
            JSONArray copyResults = new JSONArray();
            try (OutputStream stream = getContentResolver().openOutputStream(uri);
                 ZipOutputStream zip = new ZipOutputStream(stream)) {
                byte[] buffer = new byte[65536];
                for (PackageInfo p : apkPackages) {
                    List<String> paths = new ArrayList<>();
                    paths.add(p.applicationInfo.sourceDir);
                    if (p.applicationInfo.splitSourceDirs != null) Collections.addAll(paths, p.applicationInfo.splitSourceDirs);
                    int index = 0;
                    for (String path : paths) {
                        JSONObject result = new JSONObject();
                        result.put("package", p.packageName); result.put("source", path);
                        File file = new File(path);
                        // Check readability before creating an entry, so failures are explicit.
                        FileInputStream input;
                        try { input = new FileInputStream(file); }
                        catch (Exception e) { result.put("error", e.getClass().getSimpleName()); copyResults.put(result); continue; }
                        try (FileInputStream in = input) {
                            String entry = "apks/" + p.packageName + "/" + (index++ == 0 ? "base.apk" : file.getName());
                            zip.putNextEntry(new ZipEntry(entry));
                            int n; while ((n = in.read(buffer)) != -1) zip.write(buffer, 0, n);
                            zip.closeEntry();
                            result.put("entry", entry); result.put("bytes", file.length());
                        }
                        copyResults.put(result);
                    }
                }
                report.put("apk_copies", copyResults);
                zip.putNextEntry(new ZipEntry("report.json"));
                zip.write(report.toString(2).getBytes(StandardCharsets.UTF_8));
                zip.closeEntry();
            }
            ContentValues done = new ContentValues();
            done.put(MediaStore.Downloads.IS_PENDING, 0);
            if (getContentResolver().update(uri, done, null, null) != 1) throw new java.io.IOException("Could not finalize Downloads file");
        } catch (Exception e) { getContentResolver().delete(uri, null, null); throw e; }
        return filename;
    }
}
