# -*- coding: utf-8 -*-
import argparse
import sys
import re
import os
import codecs
import json
import logging
from collections import defaultdict
from datetime import datetime

# 定义全局常量
IMAGE_WIDTH_PIXELS = 1920
IMAGE_HEIGHT_PIXELS = 1080
DPI = 300

class log_split_and_grep:
    def file_log_content_splitter(log_file,logs_dir):
        # # 获取脚本所在目录并创建 logs 目录
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        # logs_dir = os.path.join(script_dir, 'logs')

        # 如果 logs 目录不存在，则创建它
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # 使用 codecs 打开文件，并指定 utf-8 编码，忽略解码错误
        with codecs.open(log_file, 'r', 'utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        session_started = False
        session_lines = []
        session_start_time = None

        # 正则表达式匹配时间戳格式
        time_pattern = re.compile(r'(\d{2}:\d{2}:\d{2}:\d{3})')

        for line in lines:
            # 查找会话的开始：包含 'joinWithDisplayName'
            if 'joinWithDisplayName' in line:
                # 如果之前已经有会话开始，保存当前会话并重置
                if session_started:
                    if session_start_time:
                        output_filename = "{}_session.log".format(session_start_time)
                        output_path = os.path.join(logs_dir, output_filename)
                        with codecs.open(output_path, 'w', 'utf-8') as session_file:
                            session_file.writelines(session_lines)
                        print("Session saved to {}".format(output_path))
                    
                    # 开始新的会话
                    session_lines = []
                    session_started = False
                    session_start_time = None

                # 新会话的开始
                session_started = True
                session_lines.append(line)

                # 提取时间戳，作为文件名的一部分
                match = time_pattern.search(line)
                if match:
                    session_start_time = match.group(1).replace(":", "_")
                else:
                    session_start_time = "unknown_time"

            # 如果会话已经开始，继续记录当前会话的行
            elif session_started:
                session_lines.append(line)

        # 处理最后一个会话
        if session_started and session_start_time:
            output_filename = "{}_session.log".format(session_start_time)
            output_path = os.path.join(logs_dir, output_filename)
            with codecs.open(output_path, 'w', 'utf-8') as session_file:
                session_file.writelines(session_lines)
            print("Session saved to {}".format(output_path))

    # 设置日志配置
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

    def file_log_content_grep(log_file_path,logs_dir, keyword):
        if keyword is None:
            print("Keyword is required for filtering.")
            return
        
        output_file_path = os.path.join(logs_dir, '{}_filtered_log.log'.format(keyword))
        
        # 确保目录存在（兼容旧版 Python）
        try:
            if not os.path.exists(os.path.dirname(output_file_path)):
                os.makedirs(os.path.dirname(output_file_path))
        except OSError as e:
            print("An error occurred while creating directories: {}".format(e))
            return
        
        try:
            with open(log_file_path, 'r') as log_file:
                with open(output_file_path, 'w') as output_file:
                    for line in log_file:
                        if keyword in line:
                            output_file.write(line)
            print("Filtered log lines containing '{}' have been saved to {}".format(keyword, output_file_path))
        except IOError as e:
            print("An error occurred while processing files: {}".format(e))
