# -*- coding: utf-8 -*-
import os
import re
import sys


class webrtcAnalyzeLog:
    # 函数：将日志文件拆分并保存
    def split_log_by_webrtc_init(self, log_file_path, output_dir="logs", callback=None):
        if callback is None:
            # Provide a default callback that does nothing if not provided
            callback = lambda message: None

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            callback(f"Output directory {output_dir} created.")
        callback(f"Splitting webrtc log file: 将日志文件拆分并保存到 {output_dir}")
        # 打开日志文件
        with open(log_file_path, "r") as log_file:
            current_file = None
            current_filename = None
            callback(
                'Splitting webrtc log file: 开始查找包含"WebRtcVoiceEngine::Init" 行'
            )
            # 统计匹配到的文件数量
            file_count = 0
            for line in log_file:
                # print("Processing line: {}".format(line))
                # 查找 "WebRtcVoiceEngine::Init"
                if "WebRtcVoiceEngine::Init" in line:
                    # 提取时间戳，格式假设为 [YYYY-MM-DD HH:MM:SS]
                    timestamp_match = re.search(
                        r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", line
                    )
                    if timestamp_match:
                        timestamp = (
                            timestamp_match.group(1).replace(" ", "-").replace(":", "-")
                        )
                        # 构造文件名
                        current_filename = "{}-webrtc.log".format(timestamp)
                        current_file_path = os.path.join(output_dir, current_filename)
                        # 关闭当前打开的文件
                        if current_file:
                            current_file.close()
                        # 打开新的文件
                        current_file = open(current_file_path, "w")
                        file_count += 1
                        callback(
                            'Splitting webrtc log file: 找到包含"WebRtcVoiceEngine::Init" 行，写入到:{}'.format(
                                current_filename
                            )
                        )

                # 将行写入当前打开的文件
                if current_file:
                    current_file.write(line)

            # 关闭最后一个文件
            if current_file:
                current_file.close()
        callback(
            "Splitting webrtc log file complete(have {} files)！！！".format(file_count)
        )

    # 函数：从日志文件中提取 ".mm:" 行并保存到 objc 文件
    def extract_objc_lines_from_logs(self, output_dir="logs", callback=None):
        # 定义日期时间的正则表达式
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
        if callback is None:
            # Provide a default callback that does nothing if not provided
            callback = lambda message: None

        for root, dirs, files in os.walk(output_dir):
            for file_name in files:
                if file_name.endswith("-webrtc.log"):
                    log_file_path = os.path.join(root, file_name)
                    objc_file_path = os.path.join(
                        root, file_name.replace("-webrtc.log", "-webrtc-objc.log")
                    )

                    with open(log_file_path, "r") as log_file:
                        with open(objc_file_path, "w") as objc_file:
                            is_mm_section = False  # 用于标记是否在 ".mm:" 区段中
                            for line in log_file:
                                if ".mm:" in line:
                                    is_mm_section = True  # 标记进入 .mm: 区段
                                    objc_file.write(line)  # 写入 .mm: 行
                                    # callback(f"Found .mm: line, writing to {objc_file_path}")
                                elif is_mm_section:
                                    if date_pattern.match(line):
                                        is_mm_section = (
                                            False  # 遇到新日期行，结束当前 .mm: 区段
                                        )
                                    else:
                                        objc_file.write(
                                            line
                                        )  # 如果不是日期开头，继续写入
                                        # callback(f"Writing continuation line to {objc_file_path}")
                            callback(f"Finished processing file: {file_name}")
