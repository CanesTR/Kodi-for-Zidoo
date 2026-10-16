  // Diagnostic only: records this APK's process history, never other applications.
  private static final java.util.concurrent.ExecutorService EXIT_LOG_WORKER =
      java.util.concurrent.Executors.newSingleThreadExecutor();

  private void recordExitDiagnostic(final String event, final boolean startup)
  {
    final android.content.Context context = getApplicationContext();
    final long eventTime = System.currentTimeMillis();
    final int pid = android.os.Process.myPid();
    try
    {
      EXIT_LOG_WORKER.execute(() -> {
        try
        {
          org.json.JSONObject item = new org.json.JSONObject();
          item.put("event", event);
          item.put("timestamp_ms", eventTime);
          item.put("pid", pid);
          item.put("package", context.getPackageName());
          item.put("sdk", Build.VERSION.SDK_INT);
          appendExitDiagnostic(context, item);
          if (startup)
          {
            try
            {
              if (Build.VERSION.SDK_INT >= 30)
                readOwnProcessExitHistory(context);
              else
                appendExitDiagnostic(context, new org.json.JSONObject().put("event", "exit_history_requires_android_11"));
            }
            catch (Exception unavailable)
            {
              appendExitDiagnostic(context, new org.json.JSONObject().put("event", "exit_history_unavailable")
                  .put("error", unavailable.toString()));
            }
            exportExitDiagnostics(context, pid);
          }
        }
        catch (Exception failure)
        {
          Log.w(TAG, "Exit diagnostics unavailable", failure);
        }
      });
    }
    catch (Exception failure)
    {
      Log.w(TAG, "Exit diagnostic scheduling failed", failure);
    }
  }

  private static void appendExitDiagnostic(android.content.Context context,
                                           org.json.JSONObject item) throws Exception
  {
    java.io.File file = new java.io.File(context.getFilesDir(), "kodi-exit-diagnostics.jsonl");
    if (file.length() > 262144)
    {
      java.io.File previous = new java.io.File(context.getFilesDir(), "kodi-exit-diagnostics.previous.jsonl");
      if (previous.exists() && !previous.delete()) throw new java.io.IOException("Cannot rotate diagnostic report");
      if (!file.renameTo(previous)) throw new java.io.IOException("Cannot rotate current diagnostic report");
    }
    try (java.io.FileOutputStream stream = new java.io.FileOutputStream(file, true))
    {
      stream.write((item.toString() + "\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));
      stream.getFD().sync();
    }
  }

  @android.annotation.TargetApi(30)
  private static void readOwnProcessExitHistory(android.content.Context context) throws Exception
  {
    android.app.ActivityManager manager =
        (android.app.ActivityManager) context.getSystemService(android.content.Context.ACTIVITY_SERVICE);
    if (manager == null) throw new java.io.IOException("ActivityManager unavailable");
    java.util.List<android.app.ApplicationExitInfo> history =
        manager.getHistoricalProcessExitReasons(context.getPackageName(), 0, 12);
    appendExitDiagnostic(context, new org.json.JSONObject().put("event", "exit_history_count")
        .put("count", history.size()).put("timestamp_ms", System.currentTimeMillis()));
    for (android.app.ApplicationExitInfo info : history)
    {
      org.json.JSONObject item = new org.json.JSONObject();
      item.put("event", "previous_process_exit");
      item.put("pid", info.getPid());
      item.put("process", info.getProcessName());
      item.put("timestamp_ms", info.getTimestamp());
      item.put("reason", info.getReason());
      item.put("status", info.getStatus());
      item.put("importance", info.getImportance());
      item.put("pss_kb", info.getPss());
      item.put("rss_kb", info.getRss());
      item.put("description", info.getDescription());
      appendExitDiagnostic(context, item);
    }
  }

  @android.annotation.TargetApi(29)
  private static void exportExitDiagnostics(android.content.Context context, int pid) throws Exception
  {
    if (Build.VERSION.SDK_INT < 29) return;
    String name = "kodi-process-exit-" + System.currentTimeMillis() + "-" + pid + ".txt";
    android.content.ContentValues values = new android.content.ContentValues();
    values.put(android.provider.MediaStore.MediaColumns.DISPLAY_NAME, name);
    values.put(android.provider.MediaStore.MediaColumns.MIME_TYPE, "text/plain");
    values.put(android.provider.MediaStore.MediaColumns.RELATIVE_PATH,
        android.os.Environment.DIRECTORY_DOWNLOADS + "/KodiZidooDiagnostics/");
    values.put(android.provider.MediaStore.MediaColumns.IS_PENDING, 1);
    android.content.ContentResolver resolver = context.getContentResolver();
    android.net.Uri target = resolver.insert(android.provider.MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
    if (target == null) throw new java.io.IOException("Downloads report unavailable");
    try
    {
      try (java.io.OutputStream output = resolver.openOutputStream(target, "w"))
      {
        if (output == null) throw new java.io.IOException("Cannot open Downloads report");
        for (String part : new String[]{"kodi-exit-diagnostics.previous.jsonl", "kodi-exit-diagnostics.jsonl"})
        {
          java.io.File file = new java.io.File(context.getFilesDir(), part);
          if (!file.isFile()) continue;
          try (java.io.FileInputStream input = new java.io.FileInputStream(file))
          {
            byte[] buffer = new byte[8192];
            int count;
            while ((count = input.read(buffer)) != -1) output.write(buffer, 0, count);
          }
        }
      }
      values.clear();
      values.put(android.provider.MediaStore.MediaColumns.IS_PENDING, 0);
      if (resolver.update(target, values, null, null) != 1)
        throw new java.io.IOException("Cannot publish Downloads report");
      Log.i(TAG, "Exit report saved in Download/KodiZidooDiagnostics/" + name);
    }
    catch (Exception failure)
    {
      try { resolver.delete(target, null, null); } catch (Exception ignored) { }
      throw failure;
    }
  }
