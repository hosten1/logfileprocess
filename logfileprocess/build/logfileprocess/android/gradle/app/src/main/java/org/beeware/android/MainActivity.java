package org.beeware.android;

import android.content.Intent;
import android.content.res.Configuration;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.LinearLayout;

import androidx.appcompat.app.AppCompatActivity;

import com.chaquo.python.Kwarg;
import com.chaquo.python.PyException;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.util.List;

import org.json.JSONArray;
import org.json.JSONException;

import com.lym.logfileprocess.R;

import android.widget.Toast;
import android.os.Environment;
import android.Manifest;
import android.provider.Settings;
import androidx.annotation.NonNull;
import androidx.annotation.RequiresApi;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;


public class MainActivity extends AppCompatActivity {

    private static final int REQUEST_CODE_MANAGE_STORAGE = 1001;
    private static final int REQUEST_CODE_STORAGE_PERMISSIONS = 1002;

    // To profile app launch, use `adb -s MainActivity`; look for "onCreate() start" and "onResume() completed".
    private String TAG = "MainActivity";
    private static PyObject pythonApp;

    /**
     * This method is called by `app.__main__` over JNI in Python when the BeeWare
     * app launches.
     *
     * @param app
     */
    @SuppressWarnings("unused")
    public static void setPythonApp(IPythonApp app) {
        pythonApp = PyObject.fromJava(app);
    }

    /**
     * We store the MainActivity instance on the *class* so that we can easily
     * access it from Python.
     */
    public static MainActivity singletonThis;

    protected void onCreate(Bundle savedInstanceState) {
        Log.d(TAG, "onCreate() start");
        // Change away from the splash screen theme to the app theme.
        setTheme(R.style.AppTheme);
        super.onCreate(savedInstanceState);
        // 检查是否已经获得MANAGE_EXTERNAL_STORAGE权限
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if (!Environment.isExternalStorageManager()) {
                // 如果没有权限，跳转到权限设置页面
                requestManageAllFilesAccessPermission();
            } else {
                // 已经有权限
                Toast.makeText(this, "已授予所有文件访问权限", Toast.LENGTH_SHORT).show();
                // 在这里继续你需要执行的操作
            }
        } else {
            // Android 11 以下版本
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED ||
                    ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                // 请求读写权限
                requestStoragePermissions();
            } else {
                // 已经有权限
                Toast.makeText(this, "已授予读写存储权限", Toast.LENGTH_SHORT).show();
                // 继续你需要执行的操作
            }
        }
        LinearLayout layout = new LinearLayout(this);
        this.setContentView(layout);
        singletonThis = this;

        Python py;
        if (Python.isStarted()) {
            Log.d(TAG, "Python already started");
            py = Python.getInstance();
        } else {
            Log.d(TAG, "Starting Python");
            AndroidPlatform platform = new AndroidPlatform(this);
            platform.redirectStdioToLogcat();
            Python.start(platform);
            py = Python.getInstance();

            String argvStr = getIntent().getStringExtra("org.beeware.ARGV");
            if (argvStr != null) {
                try {
                    JSONArray argvJson = new JSONArray(argvStr);
                    List<PyObject> sysArgv = py.getModule("sys").get("argv").asList();
                    for (int i = 0; i < argvJson.length(); i++) {
                        sysArgv.add(PyObject.fromJava(argvJson.getString(i)));
                    }
                } catch (JSONException e) {
                    throw new RuntimeException(e);
                }
            }
        }

        Log.d(TAG, "Running main module " + getString(R.string.main_module));
        py.getModule("runpy").callAttr(
            "run_module",
            getString(R.string.main_module),
            new Kwarg("run_name", "__main__"),
            new Kwarg("alter_sys", true)
        );

        userCode("onCreate");
        Log.d(TAG, "onCreate() complete");
    }

    protected void onStart() {
        Log.d(TAG, "onStart() start");
        super.onStart();
        userCode("onStart");
        Log.d(TAG, "onStart() complete");
    }

    protected void onResume() {
        Log.d(TAG, "onResume() start");
        super.onResume();
        userCode("onResume");
        Log.d(TAG, "onResume() complete");
    }

    protected void onPause() {
        Log.d(TAG, "onPause() start");
        super.onPause();
        userCode("onPause");
        Log.d(TAG, "onPause() complete");
    }

    protected void onStop() {
        Log.d(TAG, "onStop() start");
        super.onStop();
        userCode("onStop");
        Log.d(TAG, "onStop() complete");
    }
    protected void onDestroy() {
        Log.d(TAG, "onDestroy() start");
        super.onDestroy();
        userCode("onDestroy");
        Log.d(TAG, "onDestroy() complete");
    }
    protected void onRestart() {
        Log.d(TAG, "onRestart() start");
        super.onRestart();
        userCode("onRestart");
        Log.d(TAG, "onRestart() complete");
    }
    public void onTopResumedActivityChanged (boolean isTopResumedActivity){
        Log.d(TAG, "onTopResumedActivityChanged() start");
        super.onTopResumedActivityChanged(isTopResumedActivity);
        userCode("onTopResumedActivityChanged", isTopResumedActivity);
        Log.d(TAG, "onTopResumedActivityChanged() complete");
    }

    protected void onActivityResult(int requestCode, int resultCode, Intent data)
    {
        Log.d(TAG, "onActivityResult() start");
        super.onActivityResult(requestCode, resultCode, data);
        userCode("onActivityResult", requestCode, resultCode, data);
        if (requestCode == REQUEST_CODE_MANAGE_STORAGE) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                if (Environment.isExternalStorageManager()) {
                    // 用户已授予所有文件访问权限
                    Toast.makeText(this, "已授予所有文件访问权限", Toast.LENGTH_SHORT).show();
                    // 继续你需要执行的操作
                } else {
                    // 权限被拒绝
                    Toast.makeText(this, "所有文件访问权限被拒绝", Toast.LENGTH_SHORT).show();
                }
            }
        }
        Log.d(TAG, "onActivityResult() complete");
    }

    public void onConfigurationChanged(Configuration newConfig) {
        Log.d(TAG, "onConfigurationChanged() start");
        super.onConfigurationChanged(newConfig);
        userCode("onConfigurationChanged", newConfig);
        Log.d(TAG, "onConfigurationChanged() complete");
    }

    public boolean onOptionsItemSelected(MenuItem menuitem) {
        Log.d(TAG, "onOptionsItemSelected() start");
        PyObject pyResult = userCode("onOptionsItemSelected", menuitem);
        boolean result = (pyResult == null) ? false : pyResult.toBoolean();
        Log.d(TAG, "onOptionsItemSelected() complete");
        return result;
    }

    public boolean onPrepareOptionsMenu(Menu menu) {
        Log.d(TAG, "onPrepareOptionsMenu() start");
        PyObject pyResult = userCode("onPrepareOptionsMenu", menu);
        boolean result = (pyResult == null) ? false : pyResult.toBoolean();
        Log.d(TAG, "onPrepareOptionsMenu() complete");
        return result;
    }

    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults)
    {
        Log.d(TAG, "onRequestPermissionsResult() start");
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        userCode("onRequestPermissionsResult", requestCode, permissions, grantResults);
        Log.d(TAG, "onRequestPermissionsResult() complete");
        if (requestCode == REQUEST_CODE_STORAGE_PERMISSIONS) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                // 权限授予成功
                Toast.makeText(this, "读写存储权限已授予", Toast.LENGTH_SHORT).show();
                // 继续你需要执行的操作
            } else {
                // 权限被拒绝
                Toast.makeText(this, "读写存储权限被拒绝", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private PyObject userCode(String methodName, Object... args) {
        if (pythonApp == null) {
            // Could be a non-graphical app such as Python-support-testbed.
            return null;
        }
        try {
            if (pythonApp.containsKey(methodName)) {
                return pythonApp.callAttr(methodName, args);
            } else {
                // Handle the case where the method doesn't exist
                return null;
            }
        } catch (PyException e) {
            if (e.getMessage().startsWith("NotImplementedError")) {
                return null;
            }
            throw e;
        }
    }
    @RequiresApi(api = Build.VERSION_CODES.R)
    private void requestManageAllFilesAccessPermission() {
        Intent intent = new Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION);
        intent.setData(Uri.parse("package:" + getPackageName()));
        startActivity(intent);
    }


    private void requestStoragePermissions() {
        ActivityCompat.requestPermissions(this,
                new String[]{Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE},
                REQUEST_CODE_STORAGE_PERMISSIONS);
    }
}
