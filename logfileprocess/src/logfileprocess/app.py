# -*- coding: utf-8 -*-

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

import argparse
import sys
import re
import os
import codecs

import platform

from logfileprocess.tools.engine_log_analyze_data_png       import data_to_plot
from logfileprocess.tools.engine_log_analyze_data           import log_split_and_grep
from logfileprocess.tools.engine_log_analyze_data_prcess    import details_logs
from logfileprocess.tools.webrtc_log                        import webrtc_log
import threading


from os import environ
plt = platform.system()

lableText = None

def isAndroid():
    if plt == "Windows":
        print("Your system is Windows")
        return False
        # do x y z
    elif plt == "Linux":
        print("Your system is Linux")
        if 'ANDROID_BOOTLOGO' in environ:
            print("====================>Running on Android")
            return True
        else:
            print("Not Android OS")
            return False
         # do x y z
    elif plt == "Darwin":
        print("Your system is MacOS")
        return False
        # do x y z
    else:
        print("Unidentified system")
        return False

if isAndroid():
    # 调用 Java 的 Android API 示例
    from java import jclass

def send_msg_toJava(msg):
        if isAndroid():
        # 获取 Java 类
            MyJavaClass = jclass('org.beeware.android.MainActivity')

            # 创建类的实例
            my_java_object = MyJavaClass()

            # 调用 Java 方法
            my_java_object.onPthonCallback(msg)
        else:
            global lableText
            if lableText is not None:  # 检查 lableText 是否被正确初始化
                lableText.text = f"{lableText.text}\n{msg}"
            print("------>" + msg)

def java_start_analyze_engine_log_file(in_log_file_path,out_file_path):
    send_msg_toJava("开始拆分engine日志文件。。。")
    log_split_and_grep.file_log_content_splitter(in_log_file_path,out_file_path)

def java_start_analyze_webrtc_log_file(in_log_file_path,out_file_path):
     # 步骤1：拆分日志文件
    send_msg_toJava("开始拆分webrtc日志文件。。。")
    webrtc_log.split_log_by_webrtc_init(in_log_file_path,out_file_path)
    # 步骤2：提取.mm:日志到objc文件
    send_msg_toJava("开始提取webrtc日志中的.mm:日志到objc文件。。。")
    webrtc_log.extract_objc_lines_from_logs(out_file_path)

def java_start_analyze_engine_process_file(in_log_file_path,out_file_path):
    send_msg_toJava("开始提取日志关键信息。。。")
    details_logs.parse_logs_detail(in_log_file_path,out_file_path)
    send_msg_toJava("开始分析日志,保存在成图。。。")
    data_to_plot.process_rtc_status_send_data_logs(in_log_file_path,out_file_path)
    send_msg_toJava("开始分析发送端音频日志,保存在成图。。。")
    data_to_plot.extract_and_plot_aslevels(in_log_file_path,out_file_path)
    send_msg_toJava("开始分析接收音频日志,保存在成图。。。")
    data_to_plot.extract_and_plot_arlevels_recv(in_log_file_path,out_file_path)
    send_msg_toJava("开始分析接收和发送的音频日志,保存在成图。。。")
    data_to_plot.extract_and_plot_levels_RS(in_log_file_path,out_file_path)
    send_msg_toJava("开始分析接收到的音频其他数据信息,保存在成图。。。")
    data_to_plot.process_rtc_status_recv_data_logs(in_log_file_path,out_file_path)
    send_msg_toJava("开始分析发送方的音频其他数据信息,保存在成图。。。")
    data_to_plot.process_rtc_status_send_data_logs(in_log_file_path,out_file_path)

def java_choose_file_path(str):
    print(u"Hello, python java_choose_file_path={}".format(str))

def java_start_analyze_log_file(file_path):
    print(u"Hello,python java_start_analyze_log_file file_path={}".format(file_path))
     # 判断路径是否有双引号并去除
    if file_path.startswith('"') and file_path.endswith('"'):
        log_file_path = file_path[1:-1]  # 去除开头和结尾的双引号
    else:
        log_file_path = file_path  # 如果没有引号，保持原样

    print(u"Hello,python java_start_analyze_log_file log_file_path={}".format(log_file_path))
    # 去掉文件名，拼接成新的目录路径
    out_log_file_path = os.path.join(os.path.dirname(log_file_path), 'logs')
    send_msg_toJava(u"日志输出目录为:{}".format(out_log_file_path) )

    # # 检查目录是否存在，不存在则创建
    # if not os.path.exists(out_log_file_path):
    #     os.makedirs(out_log_file_path)

    
   # 获取文件名和扩展名
    file_name, file_extension = os.path.splitext(os.path.basename(log_file_path))
    send_msg_toJava(u"文件名:{}".format(file_name) )
    send_msg_toJava(u"扩展名:{}".format(file_extension) )
    # 先判断文件后缀是否是 .log
    if file_extension == ".log":
        # 文件是 .log 类型的，继续判断文件名
        # 判断文件名包含的内容并执行不同操作
        if "RTCEngine" in file_name:
            send_msg_toJava("文件名包含 'RTCEngine'，执行分割日志操作...")
            java_start_analyze_engine_log_file(log_file_path,out_log_file_path)
            # 执行与 RTCEngine 相关的操作
        elif "webrtc-native" in file_name:
            send_msg_toJava("文件名包含 'webrtc-native'，执行分割日志操作...")
            java_start_analyze_webrtc_log_file(log_file_path,out_log_file_path)
            # 执行与 webrtc-native 相关的操作
        elif "_session" in file_name:
            send_msg_toJava("文件名包含 '_session'，执行分析日志操作...")
            java_start_analyze_engine_process_file(log_file_path,out_log_file_path)
            # 执行与 webrtc-native 相关的操作
        else:
            send_msg_toJava("文件名不符合任何条件")
    else:
        # 文件不是 .log 类型的
        send_msg_toJava("文件后缀不是 .log，不执行操作")
    
class LogFileProcess(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        global lableText  # 引用全局变量
        if plt == "Windows" or plt == "Linux" or plt == "Darwin":
            main_box = toga.Box()

            self.main_window = toga.MainWindow(title=self.formal_name)
            # 按钮点击事件处理器 (异步)
            async def open_file_dialog(widget):
                # 使用新的 dialog 方法来打开文件选择对话框
                file_path = await self.main_window.dialog(
                    toga.OpenFileDialog(title="Select a file")
                )
                
                if file_path:
                    # 如果用户选择了文件，显示文件路径
                    self.label.text = f"Selected file: {file_path}"
                    java_start_analyze_log_file(str(file_path))
                else:
                    self.label.text = "No file selected."

            # 创建按钮并绑定事件处理器
            button = toga.Button("Select File", on_press=open_file_dialog)

            # 创建标签显示选中的文件
            self.label = toga.Label("No file selected.")
            lableText = self.label  # 赋值给全局变量

            # 创建布局
            box = toga.Box(children=[button, self.label], style=Pack(direction=COLUMN, padding=10))

            # 将布局设置为主窗口的内容
            self.main_window.content = box
            self.main_window.show()


def main():
    return LogFileProcess()
