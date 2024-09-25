# -*- coding: utf-8 -*-
import os
import re
import sys

# 函数：将日志文件拆分并保存
def split_log_by_webrtc_init(log_file_path, output_dir='logs'):
    print("Splitting log file: {}".format(log_file_path))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 打开日志文件
    with open(log_file_path, 'r') as log_file:
        print("Reading log file: {}".format(log_file_path))
        current_file = None
        current_filename = None

        for line in log_file:
            # print("Processing line: {}".format(line))
            # 查找 "WebRtcVoiceEngine::Init"
            if "WebRtcVoiceEngine::Init" in line:
                # 提取时间戳，格式假设为 [YYYY-MM-DD HH:MM:SS]
                timestamp_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
                if timestamp_match:
                    timestamp = timestamp_match.group(1).replace(' ', '-').replace(':', '-')
                    # 构造文件名
                    current_filename = "{}-webrtc.log".format(timestamp)
                    current_file_path = os.path.join(output_dir, current_filename)
                    # 关闭当前打开的文件
                    if current_file:
                        current_file.close()
                    # 打开新的文件
                    current_file = open(current_file_path, 'w')
            
            # 将行写入当前打开的文件
            if current_file:
                current_file.write(line)
        
        # 关闭最后一个文件
        if current_file:
            current_file.close()

# 函数：从日志文件中提取 ".mm:" 行并保存到 objc 文件
def extract_objc_lines_from_logs(output_dir='logs'):
    for root, dirs, files in os.walk(output_dir):
        for file_name in files:
            if file_name.endswith("-webrtc.log"):
                log_file_path = os.path.join(root, file_name)
                objc_file_path = os.path.join(root, file_name.replace("-webrtc.log", "-webrtc-objc.log"))

                with open(log_file_path, 'r') as log_file:
                    with open(objc_file_path, 'w') as objc_file:
                        for line in log_file:
                            if '.mm:' in line:
                                objc_file.write(line)

    
