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

from os import environ
plt = platform.system()

# 调用 Java 的 Android API 示例
from java import jclass

def java_start_analyze_engine_log_file(in_log_file_path,out_file_path):
    log_split_and_grep.file_log_content_splitter(in_log_file_path,out_file_path)

def java_start_analyze_webrtc_log_file(in_log_file_path,out_file_path):
     # 步骤1：拆分日志文件
    webrtc_log.split_log_by_webrtc_init(in_log_file_path,out_file_path)
    # 步骤2：提取.mm:日志到objc文件
    webrtc_log.extract_objc_lines_from_logs(out_file_path)



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
    print("日志输出目录为:", out_log_file_path)

    # # 检查目录是否存在，不存在则创建
    # if not os.path.exists(out_log_file_path):
    #     os.makedirs(out_log_file_path)

    
   # 获取文件名和扩展名
    file_name, file_extension = os.path.splitext(os.path.basename(log_file_path))
    print("文件名:", file_name)
    print("扩展名:", file_extension)
    # 先判断文件后缀是否是 .log
    if file_extension == ".log":
        # 文件是 .log 类型的，继续判断文件名
        # 判断文件名包含的内容并执行不同操作
        if "RTCEngine" in file_name:
            print("文件名包含 'RTCEngine'，执行相关操作...")
            java_start_analyze_engine_log_file(log_file_path,out_log_file_path)
            # 执行与 RTCEngine 相关的操作
        elif "webrtc-native" in file_name:
            print("文件名包含 'webrtc-native'，执行其他操作...")
            java_start_analyze_webrtc_log_file(log_file_path,out_log_file_path)
            # 执行与 webrtc-native 相关的操作
        else:
            print("文件名不符合任何条件")
    else:
        # 文件不是 .log 类型的
        print("文件后缀不是 .log，不执行操作")
    
class LogFileProcess(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        # 获取 Java 类
        MyJavaClass = jclass('org.beeware.android.MainActivity')

        # 创建类的实例
        my_java_object = MyJavaClass()

        # 调用 Java 方法
        my_java_object.onPthonCallback("John")

        # log_file_path = u"/Users/luoyongmeng/Downloads/Linkdood/声音/webrtc-native2024-09-24.log"
        # out_log_file_path = u"/Users/luoyongmeng/Downloads/Linkdood/声音/logs"
        # if plt == "Windows":
        #     print("Your system is Windows")
        # # do x y z
        # elif plt == "Linux":
        #     print("Your system is Linux")
        #     if 'ANDROID_BOOTLOGO' in environ:
        #         print("====================>Running on Android")
        #         log_file_path = u"/storage/emulated/0/pythonz/webrtc-native2024-09-24.log"
        #         out_log_file_path = u"/storage/emulated/0/pythonz/logs"
        #     else:
        #         print("Not Android OS")
        #     # do x y z
        # elif plt == "Darwin":
        #     print("Your system is MacOS")
        #     # do x y z
        # else:
        #     print("Unidentified system")

           
           
        # # 步骤1：拆分日志文件
        # webrtc_log.split_log_by_webrtc_init(log_file_path,out_log_file_path)

        # # 步骤2：提取.mm:日志到objc文件
        # webrtc_log.extract_objc_lines_from_logs(out_log_file_path)
        
        print("Log splitting and objc extraction completed.")
        main_box = toga.Box()

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()


def main():
    return LogFileProcess()
