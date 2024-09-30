package org.beeware.android;

public class ProcessLogFile {
    static private ProcessLogFile instance;
    // 定义一个接口用于回调
    public interface OnPythonCallbackListener {
        void onPythonCallback(String msg);
    }

    // 接口的实例
    private final OnPythonCallbackListener callbackListener;

    // 构造方法，接受接口实现的对象
    public ProcessLogFile(OnPythonCallbackListener listener) {
        instance = this;
        this.callbackListener = listener;
    }
    public void onPthonCallback(String msg){
        // 确保 UI 更新在主线程中进行
        // 调用回调方法将消息传递给 MainActivity
        if (callbackListener != null) {
            callbackListener.onPythonCallback(msg);
        }
    }
    public static ProcessLogFile getInstance(){
        return instance;
    }
}
