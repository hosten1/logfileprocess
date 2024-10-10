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

from logfileprocess.tools.engine_log_analyze_data_png import DataToPlot
from logfileprocess.tools.engine_log_analyze_data import log_split_and_grep
from logfileprocess.tools.engine_log_analyze_data_prcess import details_logs
from logfileprocess.tools.webrtc_log import webrtcAnalyzeLog
import subprocess
import concurrent.futures
import asyncio
import queue

from os import environ

plt = platform.system()

# log_messages = []  # 用于存储日志消息
log_box = None  # 用于存放日志的 Box
log_container = None  # 用于存放 ScrollContainer
# 创建一个线程安全的队列，用于在后台线程与主线程间传递日志消息
log_queue = queue.Queue()


def isAndroid():
    if plt == "Windows":
        # print("Your system is Windows")
        return False
        # do x y z
    elif plt == "Linux":
        print("Your system is Linux")
        if "ANDROID_BOOTLOGO" in environ:
            # print("====================>Running on Android")
            return True
        else:
            # print("Not Android OS")
            return False
        # do x y z
    elif plt == "Darwin":
        # print("Your system is MacOS")
        return False
        # do x y z
    else:
        # print("Unidentified system")
        return False


if isAndroid():
    # 调用 Java 的 Android API 示例
    from java import jclass


async def process_log_queue():
    while True:
        # 如果队列不为空，获取并处理消息
        if not log_queue.empty():
            message = log_queue.get()
            if message:
                process_log_queue_(message)  # 更新日志视图
        await asyncio.sleep(0.001)  # 每 10ms 检查一次队列


# 定期从队列中取出日志并更新到 UI 上
def process_log_queue_(message):
    if isAndroid():
        # 获取 Java 类
        # MainActivity = jclass("org.beeware.android.MainActivity")
        # # 调用静态方法获取 processLogFile 实例
        # processLogFile = MainActivity.getProcessLogFile()
        # my_java_object = MainActivity.getInstance()

        # # 调用 processLogFile 实例的方法
        # processLogFile.onPthonCallback(message)
        # # 创建类的实例
        # # my_java_object = MyJavaClass()
        # print("------>" + message)

        # # 调用 Java 方法
        # my_java_object.onPthonCallback(message)
        MainActivity = jclass("org.beeware.android.ProcessLogFile")
        # 调用静态方法获取 processLogFile 实例
        my_java_object = MainActivity.getInstance()
        # 创建类的实例
        # my_java_object = MyJavaClass()
        print("------>" + message)

        # 调用 Java 方法
        my_java_object.onPthonCallback(message)
    else:
        # global log_messages
        # log_messages.append(msg)  # 将消息添加到日志列表
        update_log_view(message)  # 更新日志视图
        print("------>" + message)


# 定时器，每隔一段时间执行一次
def start_processing_log_queue():
    loop = asyncio.get_event_loop()
    loop.create_task(process_log_queue())  # 启动日志处理任务
    # app = toga.App.app  # 获取当前的 Toga App 实例
    # app.add_periodic_task(0.1, process_log_queue_)  # 每隔 100ms 检查日志队列


def send_msg_toJava(msg):
    log_queue.put(msg)
    # if isAndroid():
    #     # 调用 Java 的 Android API 示例
    #     process_log_queue_(msg)
    # else:
    #     # 将消息放入队列，后台线程可以安全地调用此方法
    #     log_queue.put(msg)


def update_log_view(message):
    global log_box, log_container
    # 追加新的日志消息，不清空现有内容
    log_label = toga.Label(
        message, style=Pack(padding=5, font_size=12)  # 调整字体大小和宽度
    )
    log_box.add(log_label)  # 添加每条新的日志消息

    # 刷新容器并自动滚动到最底部
    log_container.content = log_box
    scroll_to_bottom()  # 自动滚动到底部


def scroll_to_bottom():
    global log_container, log_box
    # 获取日志内容的总高度
    content_height = log_box.layout.height
    # 获取 ScrollContainer 的可视高度
    visible_height = log_container.layout.height

    # 如果内容高度大于可视高度，进行滚动
    if content_height > visible_height:
        log_container.scroll_y = content_height  # 滚动到底部


def open_output_folder(folder_path):
    current_platform = platform.system()

    try:
        if current_platform == "Windows":
            # Windows: 使用 explorer 打开文件夹
            os.startfile(folder_path)
        elif current_platform == "Darwin":
            # macOS: 使用 open 打开文件夹
            subprocess.Popen(["open", folder_path])
        elif current_platform == "Linux":
            # Linux: 使用 xdg-open 打开文件夹
            subprocess.Popen(["xdg-open", folder_path])
        else:
            print("不支持的操作系统，无法打开文件夹。")
    except Exception as e:
        print(f"无法打开文件夹: {str(e)}")


def java_start_analyze_engine_log_file(in_log_file_path, out_file_path):
    send_msg_toJava("开始拆分engine日志文件。。。")
    log_split_and_grep.file_log_content_splitter(
        in_log_file_path, out_file_path, callback=send_msg_toJava
    )


def java_start_analyze_webrtc_log_file(in_log_file_path, out_file_path):
    # 步骤1：拆分日志文件
    send_msg_toJava("开始拆分webrtc日志文件。。。")
    webrtc_log = webrtcAnalyzeLog()
    webrtc_log.split_log_by_webrtc_init(
        in_log_file_path, out_file_path, callback=send_msg_toJava
    )
    # 步骤2：提取.mm:日志到objc文件
    send_msg_toJava("开始提取webrtc日志中的.mm:日志到objc文件。。。")
    webrtc_log.extract_objc_lines_from_logs(out_file_path, callback=send_msg_toJava)


def java_start_analyze_engine_process_sessions_file(in_log_file_path, out_file_path):
    send_msg_toJava("开始提取日志关键信息。。。")
    # 遍历目标文件夹
    for file_name in os.listdir(out_file_path):
        # 如果文件名包含 '_session'
        if "_session" in file_name:
            # 获取文件的完整路径
            full_file_path = os.path.join(out_file_path, file_name)

            # 确保它是一个文件而不是文件夹
            if os.path.isfile(full_file_path):
                # 构造要创建的文件夹路径
                folder_name = file_name.replace("_session", "_logs")
                logs_folder_path = os.path.join(out_file_path, folder_name)

                # 检查文件夹是否已经存在
                if not os.path.exists(logs_folder_path):
                    # 创建文件夹
                    os.makedirs(logs_folder_path)
                    print(f"Created folder: {logs_folder_path}")
                else:
                    print(f"Folder already exists: {logs_folder_path}")
                java_start_analyze_engine_process_file(full_file_path, logs_folder_path)


def java_start_analyze_engine_process_file(in_log_file_path, out_file_path):
    send_msg_toJava("开始提取日志关键信息。。。")
    detailsLogs = details_logs()
    data_to_plot = DataToPlot()
    detailsLogs.parse_logs_detail(
        in_log_file_path, out_file_path, callback=send_msg_toJava
    )
    send_msg_toJava("开始分析日志,保存在成图。。。")
    data_to_plot.process_rtc_status_send_data_logs(
        in_log_file_path, out_file_path, callback=send_msg_toJava
    )
    send_msg_toJava("开始分析发送端音频日志,保存在成图。。。")
    data_to_plot.extract_and_plot_aslevels(
        in_log_file_path, out_file_path, callback=send_msg_toJava
    )
    send_msg_toJava("开始分析接收音频日志,保存在成图。。。")
    data_to_plot.extract_and_plot_arlevels_recv(
        in_log_file_path, out_file_path, callback=send_msg_toJava
    )
    send_msg_toJava("开始分析接收和发送的音频日志,保存在成图。。。")
    data_to_plot.extract_and_plot_levels_RS(
        in_log_file_path, out_file_path, callback=send_msg_toJava
    )
    send_msg_toJava("开始分析接收到的音频其他数据信息,保存在成图。。。")
    data_to_plot.process_rtc_status_recv_data_logs(
        in_log_file_path, out_file_path, callback=send_msg_toJava
    )
    send_msg_toJava("开始分析发送方的音频其他数据信息,保存在成图。。。")
    data_to_plot.process_rtc_status_send_data_logs(
        in_log_file_path, out_file_path, callback=send_msg_toJava
    )


def java_choose_file_path(str):
    print("Hello, python java_choose_file_path={}".format(str))


def java_start_analyze_log_file(file_path):
    print("Hello,python java_start_analyze_log_file file_path={}".format(file_path))
    # 判断路径是否有双引号并去除
    if file_path.startswith('"') and file_path.endswith('"'):
        log_file_path = file_path[1:-1]  # 去除开头和结尾的双引号
    else:
        log_file_path = file_path  # 如果没有引号，保持原样

    print(
        "Hello,python java_start_analyze_log_file log_file_path={}".format(
            log_file_path
        )
    )
    # 去掉文件名，拼接成新的目录路径
    out_log_file_path = os.path.join(os.path.dirname(log_file_path), "logs")
    send_msg_toJava("日志输出目录为:{}".format(out_log_file_path))

    # # 检查目录是否存在，不存在则创建
    # if not os.path.exists(out_log_file_path):
    #     os.makedirs(out_log_file_path)

    # 获取文件名和扩展名
    file_name, file_extension = os.path.splitext(os.path.basename(log_file_path))
    send_msg_toJava("文件名:{}".format(file_name))
    send_msg_toJava("扩展名:{}".format(file_extension))
    # 先判断文件后缀是否是 .log
    if file_extension == ".log":
        # 文件是 .log 类型的，继续判断文件名
        # 判断文件名包含的内容并执行不同操作
        if "RTCEngine" in file_name:
            send_msg_toJava("文件名包含 'RTCEngine'，执行分割日志操作...")
            java_start_analyze_engine_log_file(log_file_path, out_log_file_path)
            java_start_analyze_engine_process_sessions_file(
                log_file_path, out_log_file_path
            )
            # 执行与 RTCEngine 相关的操作
        elif "webrtc-native" in file_name:
            send_msg_toJava("文件名包含 'webrtc-native'，执行分割日志操作...")
            java_start_analyze_webrtc_log_file(log_file_path, out_log_file_path)
            # 执行与 webrtc-native 相关的操作
        elif "_session" in file_name:
            send_msg_toJava("文件名包含 '_session'，执行分析日志操作...")
            java_start_analyze_engine_process_file(log_file_path, out_log_file_path)
            # 执行与 webrtc-native 相关的操作
        else:
            send_msg_toJava("文件名不符合任何条件")
    else:
        # 文件不是 .log 类型的
        send_msg_toJava("文件后缀不是 .log，不执行操作")

    send_msg_toJava("日志分析完成！")

    # 分析完成后，打开输出文件夹
    open_output_folder(out_log_file_path)


def run_async_task(file_path):
    # 获取当前事件循环
    loop = asyncio.get_event_loop()

    # 启动线程来执行 java_start_analyze_log_file
    with concurrent.futures.ThreadPoolExecutor() as executor:
        loop.run_in_executor(executor, java_start_analyze_log_file, str(file_path))


class LogFileProcess(toga.App):
    def startup(self):
        global log_box, log_container  # 引用全局变量
        self.main_window = toga.MainWindow(title=self.formal_name)

        if not isAndroid():
            # 创建一个标签用于提示信息
            self.info_label = toga.Label(
                "目前支持WebRTC和enging的日志分析\n"
                "1. 打开 .log 后缀的文件后自动开始分析。\n"
                "2. engine 相关的日志在 logs 目录下。\n"
                "3. 单独打开 logs 下关于 engine 分割后的日志可以分析某一个日志。",
                style=Pack(padding=10, font_size=12, color="black"),
            )
            # 创建按钮并绑定事件处理器，并设置背景色为蓝色，文本为白色
            button = toga.Button(
                "Select File",
                on_press=self.open_file_dialog,
                style=Pack(
                    width=200,  # 宽度200像素
                    background_color="blue",  # 背景色蓝色
                    color="white",  # 字体颜色白色
                    padding=10,
                ),
            )

            # 创建一个 Box 用于显示日志
            log_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

            # 创建一个 ScrollContainer，将其内容设置为 log_box
            log_container = toga.ScrollContainer(
                content=log_box, style=Pack(height=600, width=800)
            )  # 300 是设置的高度，你可以根据需求调整

            # 创建布局：先放按钮，后放日志显示区域
            main_box = toga.Box(
                children=[self.info_label, button, log_container],
                style=Pack(direction=COLUMN, padding=20),
            )
            # 设置主窗口内容
            self.main_window.content = main_box
            self.main_window.show()
        else:
            # 创建一个 Box 用于显示日志
            main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
            # 设置主窗口内容
            self.main_window.content = main_box
            self.main_window.show()
            # 启动定时处理日志队列的任务
        start_processing_log_queue()

    async def open_file_dialog(self, widget):
        file_path = await self.main_window.dialog(
            toga.OpenFileDialog(title="Select a file")
        )

        if file_path:
            send_msg_toJava(f"Selected file: {file_path}")
            # java_start_analyze_log_file(str(file_path))
            run_async_task(file_path)
            send_msg_toJava("Analysis started in background.")
        else:
            send_msg_toJava("No file selected.")


def main():
    return LogFileProcess()
