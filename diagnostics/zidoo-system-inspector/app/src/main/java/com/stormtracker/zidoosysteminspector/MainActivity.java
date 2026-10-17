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
import android.widget.ScrollView;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.concurrent.FutureTask;
import java.util.concurrent.TimeUnit;
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
        title.setText("Zidoo System Inspector 0.1.1");
        layout.addView(title);
        TextView explanation = new TextView(this);
        explanation.setText("Save a small caller snapshot first. It checks visible process names, recent caller PIDs, "
            + "selected Zidoo playback properties and framework filenames. Android may block process access; "
            + "the report records those restrictions. A current PID name does not prove a historical caller identity. "
            + "No settings are changed and no apps are stopped. The full APK export is available separately.");
        explanation.setTextSize(18);
        layout.addView(explanation);
        Button snapshot = new Button(this);
        snapshot.setText("Save caller snapshot (small)");
        layout.addView(snapshot);
        snapshot.setOnClickListener(v -> {
            snapshot.setEnabled(false);
            status.setText("Checking process visibility...");
            new Thread(() -> {
                try {
                    String filename = exportSnapshot();
                    runOnUiThread(() -> { status.setText("Saved: Internal storage/Download/ZidooSystemInspector/" + filename);
                        snapshot.setEnabled(true); });
                } catch (Exception e) {
                    runOnUiThread(() -> { status.setText("Could not save: " + e.getClass().getSimpleName() + ": " + e.getMessage());
                        snapshot.setEnabled(true); });
                }
            }, "caller-snapshot").start();
        });
        save = new Button(this);
        save.setText("Save full system APK ZIP (large)");
        layout.addView(save);
        status = new TextView(this);
        status.setTextSize(18);
        status.setText("Ready. No ADB or developer options required.");
        layout.addView(status);
        ScrollView scroll = new ScrollView(this);
        scroll.addView(layout);
        setContentView(scroll);
        snapshot.requestFocus();
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

    private JSONObject command(String... args) throws Exception {
        JSONObject result = new JSONObject();
        result.put("command", new JSONArray(java.util.Arrays.asList(args)));
        result.put("timestamp_ms", System.currentTimeMillis());
        java.lang.Process process = null;
        try {
            process = new ProcessBuilder(args).redirectErrorStream(true).start();
            final InputStream input = process.getInputStream();
            FutureTask<String> reader = new FutureTask<>(() -> {
                try (InputStream in = input; ByteArrayOutputStream output = new ByteArrayOutputStream()) {
                    byte[] buf = new byte[4096];
                    int n;
                    while ((n = in.read(buf)) != -1) {
                        int remaining = 65536 - output.size();
                        if (remaining > 0) output.write(buf, 0, Math.min(n, remaining));
                    }
                    return new String(output.toByteArray(), StandardCharsets.UTF_8);
                }
            });
            Thread worker = new Thread(reader, "snapshot-command-output");
            worker.setDaemon(true);
            worker.start();
            boolean completed = process.waitFor(3, TimeUnit.SECONDS);
            result.put("timed_out", !completed);
            if (!completed) process.destroyForcibly();
            if (completed) result.put("exit_code", process.exitValue());
            try { result.put("output_first_64k", reader.get(1, TimeUnit.SECONDS)); }
            catch (Exception e) { result.put("output_error", e.getClass().getSimpleName()); }
        } catch (Exception e) {
            result.put("error", e.getClass().getSimpleName() + ": " + e.getMessage());
        } finally {
            if (process != null) {
                process.destroy();
                try { process.getInputStream().close(); } catch (Exception ignored) { }
                try { process.getErrorStream().close(); } catch (Exception ignored) { }
                try { process.getOutputStream().close(); } catch (Exception ignored) { }
            }
        }
        return result;
    }

    private JSONObject readSmallFile(String path) throws Exception {
        JSONObject result = new JSONObject();
        result.put("path", path);
        try (FileInputStream in = new FileInputStream(path);
             ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buf = new byte[4096];
            int n;
            while (output.size() < 16384 && (n = in.read(buf, 0, Math.min(buf.length, 16384-output.size()))) != -1)
                output.write(buf, 0, n);
            result.put("text_first_16k", new String(output.toByteArray(), StandardCharsets.UTF_8).replace('\0', ' '));
        } catch (Exception e) { result.put("error", e.getClass().getSimpleName() + ": " + e.getMessage()); }
        return result;
    }

    private String exportSnapshot() throws Exception {
        JSONObject report = new JSONObject();
        report.put("schema", 1);
        report.put("inspector_version", "0.1.1");
        report.put("timestamp_ms", System.currentTimeMillis());
        report.put("model", Build.MODEL);
        report.put("sdk", Build.VERSION.SDK_INT);
        report.put("firmware_fingerprint", Build.FINGERPRINT);
        report.put("interpretation", "Read-only current snapshot. Android may hide processes. PID reuse or reboot prevents retrospective identity proof. Permission errors and absent PIDs are inconclusive.");
        JSONArray commands = new JSONArray();
        commands.put(command("/system/bin/ps", "-A", "-o", "PID,UID,NAME"));
        commands.put(command("/system/bin/ps", "-A"));
        report.put("process_commands", commands);
        JSONArray properties = new JSONArray();
        for (String key : new String[] {"zidoo.music.package.now", "zidoo.music.package.last",
                "zidoo.music.value.changed", "zidoo.play.video", "zidoo.boot.start.flag"}) {
            properties.put(command("/system/bin/getprop", key));
        }
        report.put("selected_playback_properties", properties);
        JSONArray files = new JSONArray();
        files.put(readSmallFile("/proc/uptime"));
        // These PIDs come from the uploaded exit reports; their current owners may differ.
        for (int pid : new int[] {2290, 12575, 28398}) {
            files.put(readSmallFile("/proc/" + pid + "/cmdline"));
            files.put(readSmallFile("/proc/" + pid + "/stat"));
        }
        report.put("proc_reads", files);
        JSONArray visible = new JSONArray();
        List<ActivityManager.RunningAppProcessInfo> processes = ((ActivityManager)getSystemService(ACTIVITY_SERVICE)).getRunningAppProcesses();
        if (processes != null) for (ActivityManager.RunningAppProcessInfo process : processes) {
            JSONObject item = new JSONObject();
            item.put("pid", process.pid); item.put("uid", process.uid); item.put("process", process.processName);
            visible.put(item);
        }
        report.put("api_visible_processes", visible);
        JSONArray candidates = new JSONArray();
        PackageManager pm = getPackageManager();
        for (PackageInfo info : pm.getInstalledPackages(0)) {
            ApplicationInfo app = info.applicationInfo;
            if ((app.flags & (ApplicationInfo.FLAG_SYSTEM | ApplicationInfo.FLAG_UPDATED_SYSTEM_APP)) == 0) continue;
            if (pm.checkPermission(FORCE_STOP, info.packageName) != PackageManager.PERMISSION_GRANTED) continue;
            JSONObject item = new JSONObject();
            item.put("package", info.packageName); item.put("declared_process", app.processName); item.put("uid", app.uid);
            item.put("stopped_flag", (app.flags & ApplicationInfo.FLAG_STOPPED) != 0);
            item.put("stopped_flag_note", "Package stopped state is not proof that no service or shared process is running.");
            candidates.put(item);
        }
        report.put("stop_capable_system_packages", candidates);
        JSONArray frameworks = new JSONArray();
        for (String dir : new String[] {"/system/framework", "/system_ext/framework", "/vendor/framework"}) {
            JSONObject directory = new JSONObject();
            directory.put("directory", dir);
            String[] names = new File(dir).list();
            if (names == null) directory.put("error", "Directory unavailable or access denied");
            else {
                java.util.Arrays.sort(names);
                JSONArray entries = new JSONArray();
                for (String name : names) if (name.endsWith(".jar")) entries.put(name);
                directory.put("jar_filenames", entries);
            }
            frameworks.put(directory);
        }
        report.put("framework_filenames_only", frameworks);
        String filename = "zidoo-caller-snapshot-" + System.currentTimeMillis() + ".txt";
        ContentValues values = new ContentValues();
        values.put(MediaStore.Downloads.DISPLAY_NAME, filename);
        values.put(MediaStore.Downloads.MIME_TYPE, "text/plain");
        values.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ZidooSystemInspector");
        values.put(MediaStore.Downloads.IS_PENDING, 1);
        Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
        if (uri == null) throw new java.io.IOException("Downloads could not create the file");
        try {
            try (OutputStream output = getContentResolver().openOutputStream(uri)) {
                if (output == null) throw new java.io.IOException("Downloads could not open the file");
                output.write(report.toString(2).getBytes(StandardCharsets.UTF_8));
            }
            ContentValues done = new ContentValues(); done.put(MediaStore.Downloads.IS_PENDING, 0);
            if (getContentResolver().update(uri, done, null, null) != 1) throw new java.io.IOException("Could not finalize report");
        } catch (Exception e) { getContentResolver().delete(uri, null, null); throw e; }
        return filename;
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

