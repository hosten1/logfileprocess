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

from logfileprocess.tools.engine_log_analyze_data_png   import extract_and_plot_aslevels
from logfileprocess.tools.engine_log_analyze_data  import file_log_content_splitter
from logfileprocess.tools.engine_log_analyze_data_prcess   import extract_json_from_logs
from logfileprocess.tools.webrtc_log   import split_log_by_webrtc_init
from logfileprocess.tools.webrtc_log   import extract_objc_lines_from_logs

from os import environ
plt = platform.system()

def hello_python(str):
    print(u"Hello, Python({})!！！！！！".format(str))
class LogFileProcess(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        log_file_path = u"/Users/luoyongmeng/Downloads/Linkdood/声音/webrtc-native2024-09-24.log"
        out_log_file_path = u"/Users/luoyongmeng/Downloads/Linkdood/声音/logs"
        if plt == "Windows":
            print("Your system is Windows")
        # do x y z
        elif plt == "Linux":
            print("Your system is Linux")
            if 'ANDROID_BOOTLOGO' in environ:
                print("====================>Running on Android")
                log_file_path = u"/storage/emulated/0/pythonz/webrtc-native2024-09-24.log"
                out_log_file_path = u"/storage/emulated/0/pythonz/logs"
            else:
                print("Not Android OS")
            # do x y z
        elif plt == "Darwin":
            print("Your system is MacOS")
            # do x y z
        else:
            print("Unidentified system")

           
           
        # 步骤1：拆分日志文件
        split_log_by_webrtc_init(log_file_path,out_log_file_path)

        # 步骤2：提取.mm:日志到objc文件
        extract_objc_lines_from_logs(out_log_file_path)
        
        print("Log splitting and objc extraction completed.")
        main_box = toga.Box()

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()


def main():
    return LogFileProcess()
