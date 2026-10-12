package com.stormtracker.zidoobridge;

import android.app.Activity;
import android.content.Intent;
import android.content.ContentValues;
import android.os.Build;
import android.os.Environment;
import android.provider.MediaStore;
import android.net.Uri;
import android.os.Bundle;
import android.os.StrictMode;
import android.widget.*;
import java.io.*;
import java.net.*;
import java.text.SimpleDateFormat;
import java.util.*;
import org.json.JSONObject;

public class DiagnosticActivity extends Activity {
    private String session = "";
    private String sessionPath = "";
    private String expectedMount = "";
    private int resumeMs;
    private boolean nativeResume;
    private boolean awaitingResult;
    private LinearLayout diagnosticLayout;
    private Button saveButton;
    private TextView output;
    private EditText pathInput;
    private final StringBuilder report = new StringBuilder();
    private volatile boolean polling;
    private volatile boolean destroyed;
    private Thread worker;
    private boolean resetting;
    private boolean experimentalSmb;
    private boolean bridgeSmb;
    private boolean experimentalZdmc;
    private CheckBox zdmcOption;
    private static final String API = "http://127.0.0.1:9529/ZidooVideoPlay/getPlayStatus";

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        android.content.SharedPreferences prefs = getSharedPreferences("bridge", MODE_PRIVATE);
        session = prefs.getString("session", "");
        sessionPath = prefs.getString("path", "");
        expectedMount = prefs.getString("expected_mount", "");
        resumeMs = prefs.getInt("resume", 0);
        nativeResume = prefs.getBoolean("native_resume", false);
        awaitingResult = prefs.getBoolean("awaiting", false);
        experimentalZdmc = prefs.getBoolean("experimental_zdmc", false);
        getWindow().setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN);
        LinearLayout layout = new LinearLayout(this);
        diagnosticLayout = layout;
        layout.setBackgroundColor(android.graphics.Color.BLACK);
        layout.setVisibility(isBridgeRequest(getIntent()) ? android.view.View.GONE : android.view.View.VISIBLE);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setFocusable(false);
        layout.setPadding(24,24,24,24);
        TextView heading = new TextView(this);
        heading.setText("Kodi for Zidoo Helper 0.2.11 — diagnostics");
        layout.addView(heading);
        zdmcOption = new CheckBox(this);
        zdmcOption.setId(107);
        zdmcOption.setText("Experimental ZDMC launch (S928 devices; test first)");
        zdmcOption.setChecked(experimentalZdmc);
        zdmcOption.setOnCheckedChangeListener((button, enabled) -> {
            if (enabled == experimentalZdmc) return;
            if (awaitingResult || resetting || polling || (worker != null && worker.isAlive())) {
                button.setChecked(experimentalZdmc);
                append("Finish or reset the pending session before changing launch mode.");
                return;
            }
            if (!getSharedPreferences("bridge", MODE_PRIVATE).edit()
                    .putBoolean("experimental_zdmc", enabled).commit()) {
                button.setChecked(experimentalZdmc);
                append("Could not save launch mode; previous mode retained.");
                return;
            }
            experimentalZdmc = enabled;
            append("Selected launch mode: " + (enabled ? "experimental ZDMCActivity" : "standard PlayerActivity"));
        });
        layout.addView(zdmcOption);
        pathInput = new EditText(this);
        pathInput.setId(101);
        pathInput.setSingleLine(true);
        pathInput.setHint("Local movie path: /storage/...");
        layout.addView(pathInput);
        Button smb = new Button(this); smb.setId(106); smb.setText("Test experimental SMB path (no Kodi update)");
        smb.setOnClickListener(v -> {
            if (awaitingResult) { append("Reset or finish the pending session before a diagnostic test."); return; }
            session = ""; expectedMount = ""; resumeMs = 0; nativeResume = true; bridgeSmb = false;
            experimentalSmb = true;
            try { launch(pathInput.getText().toString()); } finally { experimentalSmb = false; }
        }); layout.addView(smb);
        Button launch = new Button(this); launch.setId(102); launch.setText("Test Zidoo playback");
        launch.setOnClickListener(v -> { if (!awaitingResult) { session = ""; expectedMount = ""; resumeMs = 0; nativeResume = false; bridgeSmb = false; } launch(pathInput.getText().toString()); }); layout.addView(launch);
        Button stop = new Button(this); stop.setId(103); stop.setText("Stop diagnostic polling (keeps movie playing)");
        stop.setOnClickListener(v -> { polling = false; append("User stopped polling."); }); layout.addView(stop);
        Button save = new Button(this); saveButton = save; save.setId(104); save.setText("Save diagnostic report");
        save.setOnClickListener(v -> saveReport()); layout.addView(save);
        Button reset = new Button(this); reset.setId(105); reset.setText("Reset pending session (player must be closed)");
        reset.setOnClickListener(v -> resetPending()); layout.addView(reset);
        smb.setNextFocusDownId(102); smb.setNextFocusUpId(101);
        reset.setNextFocusDownId(107); reset.setNextFocusUpId(104);
        ScrollView scroll = new ScrollView(this); output = new TextView(this);
        pathInput.setNextFocusDownId(106); pathInput.setNextFocusUpId(107);
        zdmcOption.setNextFocusDownId(101); zdmcOption.setNextFocusUpId(105);
        launch.setNextFocusDownId(103); launch.setNextFocusUpId(106);
        stop.setNextFocusDownId(104); stop.setNextFocusUpId(102);
        save.setNextFocusDownId(105); save.setNextFocusUpId(103);
        output.setTextIsSelectable(false); output.setFocusable(false);
        scroll.setFocusable(false); scroll.addView(output);
        layout.addView(scroll,new LinearLayout.LayoutParams(-1,0,1)); setContentView(layout); save.requestFocus();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(openFileInput("latest-report.txt"), "UTF-8"))) {
            String line; while ((line = reader.readLine()) != null) report.append(line).append('\n');
        } catch (FileNotFoundException ignored) {
        } catch (Exception e) { report.append("Checkpoint recovery failed: ").append(e).append('\n'); }
        append("Helper 0.2.11 opened. Previous diagnostic checkpoint retained.");
        append("DEVICE: Android=" + Build.VERSION.RELEASE + " API=" + Build.VERSION.SDK_INT + " model=" + Build.MODEL + " manufacturer=" + Build.MANUFACTURER + " firmware=" + Build.DISPLAY);
        append("PLAYER MODE: " + (experimentalZdmc ? "experimental ZDMCActivity" : "standard PlayerActivity"));
        append("HELPER TASK: id=" + getTaskId() + " root=" + isTaskRoot() + " incoming_flags=" + getIntent().getFlags());
        append("No root or shell commands. Android 6–9 requires storage permission for Downloads export.");
        if (state == null && ensureLegacyStorage()) receive(getIntent());
    }
    @Override protected void onResume() {
        super.onResume();
        if (saveButton != null) saveButton.requestFocus();
    }
    @Override public void onNewIntent(Intent intent) { super.onNewIntent(intent); setIntent(intent); receive(intent); }
    private boolean isBridgeRequest(Intent intent) {
        Uri uri = intent == null ? null : intent.getData();
        return uri != null && "zidoobridge".equals(uri.getScheme()) && "play".equals(uri.getHost());
    }
    private void receive(Intent intent) {
        if (diagnosticLayout != null && isBridgeRequest(intent))
            diagnosticLayout.setVisibility(android.view.View.GONE);
        Uri uri = intent.getData();
        if (uri == null) return;
        if (!"zidoobridge".equals(uri.getScheme()) || !"play".equals(uri.getHost())) {
            append("Rejected unexpected request URI."); return;
        }
        if (resetting) { append("Session reset check in progress; retry after it finishes."); return; }
        if (!ensureLegacyStorage()) return;
        String path = uri.getQueryParameter("path");
        String requestedSession = uri.getQueryParameter("session");
        if (awaitingResult) { append("Player result still pending for the current session."); return; }
        if (requestedSession != null && !requestedSession.matches("[a-f0-9]{32}")) {
            append("Rejected invalid session identifier."); return;
        }
        String requestedMount = uri.getQueryParameter("expected_mount");
        requestedMount = requestedMount == null ? "" : requestedMount;
        if (!requestedMount.isEmpty() && !MediaPath.validPinnedMount(path, requestedMount)) {
            append("Rejected invalid pinned SMB mount identity."); return;
        }
        expectedMount = requestedMount;
        session = requestedSession == null ? "" : requestedSession;
        sessionPath = path == null ? "" : path;
        try {
            String offset = uri.getQueryParameter("resume_ms");
            resumeMs = offset == null ? 0 : Integer.parseInt(offset);
            if (resumeMs < 0) throw new IllegalArgumentException("Negative resume");
        } catch (Exception e) { append("Rejected invalid resume position."); session = ""; return; }
        nativeResume = "1".equals(uri.getQueryParameter("native_resume"));
        bridgeSmb = "1".equals(uri.getQueryParameter("allow_smb"));
        if (path != null) { pathInput.setText(path); launch(path); }
    }
    private void persistSession() {
        if (!getSharedPreferences("bridge", MODE_PRIVATE).edit().putString("session", session)
                .putString("expected_mount", expectedMount).putString("path", sessionPath).putInt("resume", resumeMs).putBoolean("native_resume", nativeResume)
                .putBoolean("awaiting", awaitingResult).commit())
            throw new IllegalStateException("Could not checkpoint playback session");
    }
    private boolean ensureLegacyStorage() {
        if (Build.VERSION.SDK_INT >= 29 || checkSelfPermission(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
                == android.content.pm.PackageManager.PERMISSION_GRANTED) return true;
        requestPermissions(new String[]{android.Manifest.permission.WRITE_EXTERNAL_STORAGE}, 71);
        return false;
    }
    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(requestCode, permissions, results);
        if (requestCode != 71) return;
        if (results.length > 0 && results[0] == android.content.pm.PackageManager.PERMISSION_GRANTED) {
            append("Legacy Downloads storage permission granted.");
            if (isBridgeRequest(getIntent())) receive(getIntent());
            else append("Select Test playback or Save diagnostic report to continue.");
        } else {
            if (diagnosticLayout != null) diagnosticLayout.setVisibility(android.view.View.VISIBLE);
            append("Storage permission denied. Allow storage permission in Android app settings to export reports and playback results.");
        }
    }
    private Uri exportLegacy(String name, String text) throws IOException {
        if (checkSelfPermission(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
                != android.content.pm.PackageManager.PERMISSION_GRANTED)
            throw new IOException("Storage permission is required for Downloads export");
        if (!Environment.MEDIA_MOUNTED.equals(Environment.getExternalStorageState()))
            throw new IOException("Shared storage is unavailable");
        File directory = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "ZidooBridge");
        if (!directory.isDirectory() && !directory.mkdirs()) throw new IOException("Could not create " + directory);
        File destination = new File(directory, name);
        if (!destination.getCanonicalFile().getParentFile().equals(directory.getCanonicalFile()))
            throw new IOException("Invalid export filename");
        File temporary = File.createTempFile("bridge-", ".tmp", directory);
        try {
            try (FileOutputStream out = new FileOutputStream(temporary)) {
                out.write(text.getBytes("UTF-8"));
                out.getFD().sync();
            }
            if (!temporary.renameTo(destination)) throw new IOException("Could not publish " + destination);
            return Uri.fromFile(destination);
        } finally { if (temporary.exists()) temporary.delete(); }
    }
    private Uri exportJson(String name, JSONObject obj) throws Exception {
        if (Build.VERSION.SDK_INT < 29) return exportLegacy(name, obj.toString());
        ContentValues values = new ContentValues();
        values.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
        values.put(MediaStore.MediaColumns.MIME_TYPE, "application/json");
        values.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ZidooBridge/");
        values.put(MediaStore.MediaColumns.IS_PENDING, 1);
        Uri file = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
        if (file == null) throw new IOException("No Downloads URI");
        try {
            try (OutputStream out = getContentResolver().openOutputStream(file, "w")) {
                if (out == null) throw new IOException("No Downloads stream");
                out.write(obj.toString().getBytes("UTF-8"));
            }
            values.clear(); values.put(MediaStore.MediaColumns.IS_PENDING, 0);
            if (getContentResolver().update(file, values, null, null) != 1)
                throw new IOException("Could not publish result");
            return file;
        } catch (Exception e) {
            try { getContentResolver().delete(file, null, null); } catch (Exception ignored) {}
            throw e;
        }
    }
    private JSONObject sessionMessage(String status) throws Exception {
        JSONObject obj = new JSONObject();
        obj.put("schema", 1); obj.put("session", session); obj.put("path", sessionPath);
        obj.put("status", status); obj.put("helper_version", "0.2.11");
        obj.put("native_resume", nativeResume); obj.put("expected_mount", expectedMount);
        obj.put("timestamp_ms", System.currentTimeMillis()); return obj;
    }
    private void returnToKodi() {
        // Kodi 22 exposes Main separately from the launcher Splash activity.
        // Avoid the launcher path when returning from an existing session.
        try {
            Intent kodi = new Intent(Intent.ACTION_MAIN);
            kodi.setClassName("org.xbmc.kodi", "org.xbmc.kodi.Main");
            getPackageManager().getActivityInfo(kodi.getComponent(), 0);
            kodi.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK
                    | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT
                    | Intent.FLAG_ACTIVITY_SINGLE_TOP
                    | Intent.FLAG_ACTIVITY_NO_ANIMATION);
            append("RETURN: direct Kodi Main");
            startActivity(kodi);
            finish();
        } catch (Exception directError) {
            append("Direct Kodi return unavailable: " + directError);
            try {
                Intent kodi = getPackageManager().getLaunchIntentForPackage("org.xbmc.kodi");
                if (kodi == null) throw new IOException("Kodi launch activity unavailable");
                kodi.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK
                        | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT
                        | Intent.FLAG_ACTIVITY_SINGLE_TOP
                        | Intent.FLAG_ACTIVITY_NO_ANIMATION);
                append("RETURN: Kodi launcher fallback");
                startActivity(kodi);
                finish();
            } catch (Exception e) { append("Return to Kodi manually: " + e); }
        }
    }
    private void handlePlayerResult(int result, Intent data) {
        polling = false;
        if (worker != null) worker.interrupt();
        if (session.isEmpty() || !awaitingResult) {
            append("DIAGNOSTIC PLAYER RESULT: code=" + result + " has_data=" + (data != null)
                    + " position_ms=" + (data == null ? -1 : data.getIntExtra("position", -1))
                    + " duration_ms=" + (data == null ? -1 : data.getIntExtra("duration", -1))
                    + " end_by=" + (data == null ? null : data.getStringExtra("end_by"))
                    + " url=" + (data == null ? null : data.getStringExtra("url")));
            if (data != null && data.getExtras() != null)
                append("DIAGNOSTIC RESULT KEYS: " + data.getExtras().keySet());
            saveReport(false); return;
        }
        try {
            JSONObject obj = sessionMessage("error");
            String path = data == null ? null : data.getStringExtra("url");
            int position = data == null ? -1 : data.getIntExtra("position", -1);
            int duration = data == null ? -1 : data.getIntExtra("duration", -1);
            String end = data == null ? null : data.getStringExtra("end_by");
            boolean valid = result == RESULT_OK && MediaPath.sameResult(sessionPath, path, expectedMount) && duration > 0
                && position >= 0 && position <= duration && end != null;
            obj.put("result_code", result); obj.put("returned_path", path == null ? "" : path);
            obj.put("position_ms", position); obj.put("duration_ms", duration);
            obj.put("end_by", end == null ? "" : end);
            obj.put("status", valid ? "completed" : "error");
            if (!valid) obj.put("error", "Missing, mismatched, or invalid native result; library must remain unchanged");
            exportJson("bridge-result-" + session + ".json", obj);
            append("BRIDGE RESULT published: " + obj);
            awaitingResult = false; persistSession();
            saveReport(false);
            returnToKodi();
        } catch (Exception e) { append("BRIDGE RESULT EXPORT ERROR: " + e); }
    }
    private Uri checkedSmb(String path) {
        if (path == null || path.indexOf('\0') >= 0) return null;
        Uri uri = Uri.parse(path.replace(" ", "%20"));
        try { MediaPath.smbMount(path); } catch (Exception invalid) { return null; }
        String decoded = uri.getPath();
        if (!"smb".equals(uri.getScheme()) || uri.getHost() == null || uri.getHost().isEmpty()
                || uri.getAuthority() == null || uri.getAuthority().contains("@")
                || uri.getQuery() != null || uri.getFragment() != null || decoded == null
                || decoded.indexOf('\0') >= 0 || decoded.contains("\\") || decoded.contains("/../")
                || decoded.endsWith("/..") || decoded.contains("/./") || decoded.endsWith("/")) return null;
        String[] parts = decoded.split("/");
        if (parts.length < 3 || parts[1].isEmpty()) return null;
        String lower = parts[parts.length - 1].toLowerCase(Locale.US);
        if (!lower.matches(".+\\.(mkv|mp4|m4v|avi|mov|ts|m2ts|mts|mpg|mpeg|iso|vob|wmv|webm)")) return null;
        return uri;
    }
    private void resetPending() {
        if (resetting || polling || (worker != null && worker.isAlive())) {
            append("Reset blocked: stop diagnostic polling and wait for it to finish first."); return;
        }
        if (!ensureLegacyStorage()) return;
        resetting = true;
        final String expectedSession = session;
        append("Checking native player status before resetting; no library changes will be made.");
        new Thread(() -> {
            HttpURLConnection conn = null;
            try {
                conn = (HttpURLConnection)new URL(API).openConnection();
                conn.setConnectTimeout(2000); conn.setReadTimeout(2000);
                if (conn.getResponseCode() != 200) throw new IOException("Player status HTTP request failed");
                StringBuilder body = new StringBuilder();
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"))) {
                    char[] buffer = new char[4096]; int count;
                    while ((count = reader.read(buffer)) != -1) {
                        if (body.length() + count > 262144) throw new IOException("Player status response too large");
                        body.append(buffer, 0, count);
                    }
                }
                Object status = new JSONObject(body.toString()).opt("status");
                if (!(status instanceof Number) || ((Number)status).doubleValue() != 806.0)
                    throw new IOException("Player is active or status is unrecognized; close playback first");
                runOnUiThread(() -> {
                    try {
                        if (destroyed || !session.equals(expectedSession) || polling
                                || (worker != null && worker.isAlive()))
                            throw new IOException("Session changed during reset check; retry");
                        if (!session.isEmpty() && awaitingResult) {
                            JSONObject cancelled = sessionMessage("error");
                            cancelled.put("returned_path", sessionPath); cancelled.put("result_code", 0);
                            cancelled.put("error", "Pending session reset by user while player reported idle; no library update");
                            exportJson("bridge-result-" + session + ".json", cancelled);
                        }
                        awaitingResult = false; session = ""; sessionPath = ""; expectedMount = ""; resumeMs = 0;
                        persistSession();
                        append("Pending session reset. Kodi will reject the cancelled result without updating resume or watched state.");
                        saveReport(false);
                    } catch (Exception e) { append("RESET ERROR: " + e); }
                    finally { resetting = false; }
                });
            } catch (Exception e) {
                append("RESET BLOCKED: " + e);
                runOnUiThread(() -> { resetting = false; });
            } finally { if (conn != null) conn.disconnect(); }
        }, "ZidooResetCheck").start();
    }
    private void launch(String path) {
        if (!ensureLegacyStorage()) return;
        if (resetting || awaitingResult || polling || (worker != null && worker.isAlive())) { append("Diagnostic already running."); return; }
        Uri smbUri = (experimentalSmb || bridgeSmb) ? checkedSmb(path) : null;
        if ((experimentalSmb || bridgeSmb) && smbUri == null) {
            append("Rejected SMB test: enter a complete smb://host/share/folder/movie.mkv path without login, password, query or fragment. Folders alone are not accepted."); return;
        }
        if (smbUri == null && (path == null || !path.startsWith("/storage/") || path.indexOf('\0') >= 0 || path.contains("/../"))) {
            append("Rejected: select a local /storage/... movie. Use the separate experimental SMB test button for network diagnostics."); return;
        }
        if (!session.isEmpty()) {
            try {
                sessionPath = path;
                exportJson("bridge-ready-" + session + ".json", sessionMessage("ready"));
                awaitingResult = true; persistSession();
            } catch (Exception e) { awaitingResult = false; append("BRIDGE PREPARATION ERROR: " + e); return; }
        }
        append("Selected path: " + path);
        Intent player = new Intent(Intent.ACTION_VIEW);
        player.setClassName("com.zidoo.player", experimentalZdmc
                ? "com.zidoo.player.activity.ZDMCActivity"
                : "com.zidoo.player.activity.PlayerActivity");
        if (experimentalZdmc) {
            player.putExtra("play_mode", "zdmc");
            player.putExtra("MEDIA_BROWSER_USE_RT_MEDIA_PLAYER", "true");
            player.putExtra("SourceFrom", "Local");
            player.putExtra("net_mode", smbUri == null ? "local" : "smb");
        }
        append("PLAYER COMPONENT: " + player.getComponent().flattenToString()
                + (experimentalZdmc ? " play_mode=zdmc; experimental result compatibility" : ""));
        player.setDataAndType(smbUri == null ? Uri.fromFile(new File(path)) : smbUri,"video/*");
        append("LAUNCH MODE: " + (smbUri == null ? "local storage" : (session.isEmpty() ? "experimental SMB diagnostic; no Kodi update" : "experimental SMB library session; verified native result required")));
        // Task-preservation experiment: retain the result relationship without
        // asking Android to clear or reset the native player's activity stack.
        player.setFlags(0);
        player.putExtra("return_result", true);
        if (!nativeResume) {
            player.putExtra("from_start", resumeMs == 0);
            if (resumeMs > 0) player.putExtra("position", resumeMs);
        }
        append("RESUME MODE: " + (nativeResume ? "Zidoo native history/dialog (no from_start or position extras)" : "Explicit Kodi bookmark"));
        // File URI experiment affects this helper's VM diagnostics only; it grants no file access.
        StrictMode.VmPolicy previous = StrictMode.getVmPolicy();
        try {
            StrictMode.setVmPolicy(new StrictMode.VmPolicy.Builder().build());
            append("Intent: " + player.toUri(0));
            append("NATIVE HANDOFF: flags=" + player.getFlags() + " helper_task=" + getTaskId());
            startActivityForResult(player,42);
            append("Launch request accepted; playback remains unconfirmed.");
        } catch (Exception e) {
            StringWriter trace = new StringWriter(); e.printStackTrace(new PrintWriter(trace));
            append("LAUNCH ERROR: " + trace);
            if (!session.isEmpty()) {
                try {
                    JSONObject obj = sessionMessage("error"); obj.put("error", e.toString());
                    exportJson("bridge-result-" + session + ".json", obj);
                    awaitingResult = false; persistSession(); returnToKodi();
                } catch (Exception failure) { append("Launch failure export error: " + failure); }
            }
            return;
        } finally { StrictMode.setVmPolicy(previous); }
        polling = true;
        worker = new Thread(() -> {
            long lastPosition = -1; boolean sawAdvance = false;
            for (int i=0; i<60 && polling && !destroyed; i++) {
                HttpURLConnection conn = null;
                try {
                    conn = (HttpURLConnection)new URL(API).openConnection();
                    conn.setConnectTimeout(2000); conn.setReadTimeout(2000);
                    int status = conn.getResponseCode();
                    InputStream in = status >= 400 ? conn.getErrorStream() : conn.getInputStream();
                    if(in == null) throw new IOException("No response body");
                    StringBuilder body = new StringBuilder();
                    try(BufferedReader reader = new BufferedReader(new InputStreamReader(in,"UTF-8"))) {
                        String line; while((line=reader.readLine())!=null && body.length()<262144) body.append(line);
                    }
                    append("SAMPLE " + i + " HTTP " + status + " RAW " + body);
                    JSONObject obj = new JSONObject(body.toString()); JSONObject video = obj.optJSONObject("video");
                    if (obj.optInt("status") == 200 && video != null && video.optLong("duration",0)>0) {
                        long position = video.optLong("currentPosition",-1);
                        if(lastPosition>=0 && position>lastPosition) { sawAdvance=true; append("Position advanced; video duration="+video.optLong("duration")); }
                        lastPosition = position;
                    } else if (obj.optInt("status") == 806 && sawAdvance) { append("Idle after advancing playback."); break; }
                } catch(Exception e) { append("POLL ERROR: " + e); }
                finally { if(conn!=null)conn.disconnect(); }
                try { Thread.sleep(3000); } catch(InterruptedException e) { break; }
            }
            polling=false; append("Polling finished. Save this report. Advancing playback captured="+sawAdvance);
        },"ZidooDiagnostic"); worker.start();
    }
    private void saveReport() { saveReport(true); }
    private void saveReport(boolean showDialog) {
        if (!ensureLegacyStorage()) return;
        String name = "zidoo-helper-report-" + new SimpleDateFormat("yyyyMMdd-HHmmss-SSS", Locale.US).format(new Date()) + ".txt";
        Uri saved = null;
        try {
            if (Build.VERSION.SDK_INT < 29) {
                String snapshot;
                synchronized (report) { snapshot = report.toString(); }
                Uri legacy = exportLegacy(name, snapshot);
                append("REPORT SAVED: " + legacy.getPath());
                if (showDialog) new android.app.AlertDialog.Builder(this).setTitle("Diagnostic report saved")
                    .setMessage("Internal storage: " + legacy.getPath()).setPositiveButton("OK", null).show();
                return;
            }
            ContentValues values = new ContentValues();
            values.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            values.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain");
            values.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/ZidooBridge/");
            values.put(MediaStore.MediaColumns.IS_PENDING, 1);
            saved = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
            if (saved == null) throw new IOException("Downloads provider returned no file URI");
            String snapshot;
            synchronized (report) { snapshot = report.toString(); }
            try (OutputStream out = getContentResolver().openOutputStream(saved, "w")) {
                if (out == null) throw new IOException("Downloads provider returned no output stream");
                out.write(snapshot.getBytes("UTF-8"));
            }
            ContentValues complete = new ContentValues();
            complete.put(MediaStore.MediaColumns.IS_PENDING, 0);
            if (getContentResolver().update(saved, complete, null, null) != 1)
                throw new IOException("Could not publish the saved report");
            String location = Environment.DIRECTORY_DOWNLOADS + "/ZidooBridge/" + name;
            append("REPORT SAVED: " + location);
            if (showDialog) new android.app.AlertDialog.Builder(this).setTitle("Diagnostic report saved")
                .setMessage("Internal storage: " + location).setPositiveButton("OK", null).show();
        } catch (Exception e) {
            if (saved != null) {
                try { getContentResolver().delete(saved, null, null); } catch (Exception ignored) {}
            }
            append("SAVE ERROR: " + e);
            if (showDialog) new android.app.AlertDialog.Builder(this).setTitle("Report could not be saved")
                .setMessage(e.toString()).setPositiveButton("OK", null).show();
        }
    }
    private void append(String value) {
        String snapshot;
        synchronized(report) {
            report.append(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss",Locale.US).format(new Date())).append(" ").append(value).append('\n');
            snapshot=report.toString();
            try(FileOutputStream f = openFileOutput("latest-report.txt",MODE_PRIVATE)) { f.write(snapshot.getBytes("UTF-8")); } catch(Exception ignored) {}
        }
        final String text=snapshot; runOnUiThread(() -> { if(!destroyed) {
            output.setText(text);
            // Keep diagnostics accessible if automatic playback cannot continue.
            if (value.startsWith("LAUNCH ERROR") || value.startsWith("BRIDGE PREPARATION ERROR") || value.startsWith("BRIDGE RESULT EXPORT ERROR") || value.startsWith("Rejected") ||
                value.startsWith("Player result still pending") || value.startsWith("Return to Kodi manually"))
                diagnosticLayout.setVisibility(android.view.View.VISIBLE);
        } });
    }
    @Override protected void onActivityResult(int request,int result,Intent data) {
        super.onActivityResult(request,result,data);
        if(request==42) {
            append("Player returned result="+result+" data="+(data==null?"null":data.toUri(0)));
            boolean bridgeResult = !session.isEmpty() && awaitingResult;
            handlePlayerResult(result, data);
            if (!bridgeResult) saveReport(false);
        }
    }
    @Override protected void onDestroy() { destroyed=true; polling=false; if(worker!=null)worker.interrupt(); super.onDestroy(); }
}
