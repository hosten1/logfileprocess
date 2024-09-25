# -*- coding: utf-8 -*-
import re
import codecs
import os
import json
from datetime import datetime
# 分析socketio发送数据相关  开始
def extract_json_from_logs(log_lines):
    extracted_logs = []  # 存储提取出来的日志
    for i, line in enumerate(log_lines):
        if 'sendMessage' in line:
            # 找到包含 sendMessage 的行
            print(u"找到日志行: {}".format(line))

            before_json_part = line.split('{')[0].strip()  # 提取 { 之前的内容
            json_lines = []  # 存储 JSON 部分的行
            # //如果一行有完整的 直接处理
            if line.find('{') != -1 and re.search(r'}\s*(array|method)?', line):
                print(u"找到日志行: {}".format(line))
                 # 将结果存储为字典并添加到数组
                extracted_logs.append({
                    "before_json": line,
                    "json": "",
                    "after_json": ""
                })
                continue
            # 找到 JSON 开始的部分
            json_start_index = line.find('{')
            if json_start_index != -1:
                json_lines.append(line[json_start_index:].strip())
                
                # 标志 JSON 开始
                json_started = True
                after_json_part = ''  # 初始化 JSON 之后的部分
                for j in range(i + 1, len(log_lines)):
                    current_line = log_lines[j].strip()

                    if json_started:
                        # 检查 JSON 是否结束
                        if re.search(r'}\s*(array|method)?', current_line):
                            # JSON 部分结束，分割行内容
                            json_end_split = current_line.split('}', 1)
                            json_lines.append(json_end_split[0] + "}")  # 保留 } 作为 JSON 的一部分
                            after_json_part = json_end_split[1].strip() if len(json_end_split) > 1 else ''
                            break
                        else:
                            json_lines.append(current_line)

            # 拼接所有 JSON 行为一个完整的字符串
            full_json_str = ' '.join(json_lines)

            # 将结果存储为字典并添加到数组
            extracted_logs.append({
                "before_json": before_json_part,
                "json": full_json_str,
                "after_json": after_json_part
            })

    return extracted_logs

def analyze_logs_from_file(log_file_path):
    with codecs.open(log_file_path, 'r', 'utf-8') as log_file:
        log_lines = log_file.readlines()

    extracted_logs = extract_json_from_logs(log_lines)

    output_filename = "{}_analyze_process.log".format(os.path.splitext(log_file_path)[0])

    if not os.path.exists('logs'):
        os.makedirs('logs')

    with codecs.open(output_filename, 'w', 'utf-8') as f:
        for log in extracted_logs:
            f.write(u"Before JSON: {}\n".format(log["before_json"]))
            f.write(u"Extracted JSON: {}\n".format(log["json"]))
            f.write(u"After JSON: {}\n".format(log["after_json"]))
            f.write(u"---------------------------\n")

    print("日志分析结果已保存到: {}".format(output_filename))

# 分析socketio发送数据相关  结束


def parse_logs_detail(input_file_path, output_file_name="output_results.json"):
    # 确保 logs 目录存在
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # 设置输出文件路径
    output_file_path = os.path.join(logs_dir, output_file_name)

    results = {
        "createTransport": [],
        "join": {},
        "verify_msg": {},
        "queryRoom": {},
        "joinRoomInternal": {},
        "error_line": []
    }

    time_pattern = r'\[(\d{2}:\d{2}:\d{2}:\d{3})'

    # 读取日志文件
    with open(input_file_path, 'r') as input_file:
        log_lines = input_file.readlines()

    # Step 1: 处理 joinRoomInternal
    for line in log_lines:
        if 'joinRoomInternalWithDisplayName(begin)' in line:
            start_time_match = re.search(time_pattern, line)
            if start_time_match:
                start_time = start_time_match.group(1)

            # 寻找 joinRoomInternalWithDisplayName(end) 行
            for next_line in log_lines:
                if 'joinRoomInternalWithDisplayName(end)' in next_line:
                    server_info_match = re.search(r'serverInfo:(http[s]?://[^ ]+)', next_line)
                    if server_info_match:
                        server_addr = server_info_match.group(1)
                        app_info_match = re.search(r'appInfo：(\{.*\})', next_line)
                        if app_info_match:
                            app_info = app_info_match.group(1)

                            # 处理 app_info
                            app_info = app_info.replace('=', ':').replace('(', '[').replace(')', ']')
                            app_info = json.loads(app_info)

                            results['joinRoomInternal'] = {
                                "server_ip": server_addr,
                                "app_info": app_info,
                                "start_time": start_time
                            }
                    break

            break

    # Step 2: 查找 _protoo Peer "open" event
    for line in log_lines:
        if '_protoo Peer "open" event' in line:
            open_time_match = re.search(time_pattern, line)
            if open_time_match:
                results['joinRoomInternal']['end_time'] = open_time_match.group(1)
            break

    # Step 3: 查找 Verify msg:
    for line in log_lines:
        if 'Verify msg:' in line:
            verify_time_match = re.search(time_pattern, line)
            if verify_time_match:
                results['verify_msg'] = {
                    'verify_time': verify_time_match.group(1),
                    'end_time': "",
                    'duration': 0
                }
            break

    # Step 4: 处理 queryRoom
    for idx, line in enumerate(log_lines):
        if 'sending mediasoup request [method:queryRoom]' in line:
            query_room_start_time_match = re.search(time_pattern, line)
            if query_room_start_time_match:
                results['queryRoom']['start_time'] = query_room_start_time_match.group(1)

                # 查找对应的 callback
                for cb_line in log_lines[idx:]:
                    if 'sendMessage(method = queryRoom)' in cb_line and 'callback:respData' in cb_line:
                        query_room_end_time_match = re.search(time_pattern, cb_line)
                        if query_room_end_time_match:
                            results['queryRoom']['end_time'] = query_room_end_time_match.group(1)
                        break
                break

    # Step 5: 处理 join
    for idx, line in enumerate(log_lines):
        if 'sending mediasoup request [method:join]' in line:
            join_start_time_match = re.search(time_pattern, line)
            if join_start_time_match:
                results['join']['start_time'] = join_start_time_match.group(1)

                # 查找对应的 callback 并提取 JSON 数据
                for cb_idx, cb_line in enumerate(log_lines[idx:]):
                    if 'callback:respData' in cb_line and 'method:join' in cb_line:
                        join_end_time_match = re.search(time_pattern, cb_line)
                        if join_end_time_match:
                            results['join']['end_time'] = join_end_time_match.group(1)
                            json_str = parse_logs_detail_extract_json(log_lines, cb_idx + idx)
                            json_str = json_str.replace('=', ':').replace('(', '[').replace(')', ']')
                            results['join']['resp_data'] = json.loads(json_str)
                        break
                break

    # Step 6: 处理 createTransport
    transports = {}

    # 处理 createTransport
    for line in log_lines:
        if 'createTransport()' in line:
            direction_match = re.search(r'direction:\((\w+)\)', line)
            if direction_match:
                direction = direction_match.group(1)
                start_time_match = re.search(time_pattern, line)
                if start_time_match:
                    start_time = start_time_match.group(1)
                    transport_entry = {
                        'direction': direction,
                        'start_time': start_time,
                        'connected_time': '',
                        'connected_state': '',
                        'disconnected_time': '',
                        'disconnected_state': ''
                    }
                    transports[direction] = transport_entry

    # 收集每个方向的事件
    for line in log_lines:
        if 'Transport connection state changed to' in line:
            direction_match = re.search(r'direction:\s*(\w+)', line)
            if direction_match:
                direction = direction_match.group(1)
                if direction in transports:
                    state_time_match = re.search(time_pattern, line)
                    if state_time_match:
                        state = re.search(r'Transport connection state changed to\s+(\w+)', line).group(1)
                        state_time = state_time_match.group(1)
                        if state == 'connected':
                            transports[direction]['connected_time'] = state_time
                            transports[direction]['connected_state'] = state
                        else:
                            transports[direction]['disconnected_time'] = state_time
                            transports[direction]['disconnected_state'] = state
    # 计算每个事件的持续时间
    def calculate_duration(start_time, end_time):
        start = map(int, start_time.split(':'))
        end = map(int, end_time.split(':'))
        start_ms = sum([x * y for x, y in zip(start, [3600000, 60000, 1000, 1])])
        end_ms = sum([x * y for x, y in zip(end, [3600000, 60000, 1000, 1])])
        return end_ms - start_ms


    # 组织结果
    for direction, transport in transports.items():
        connected_time = transport['connected_time']
        disconnected_time = transport['disconnected_time']

        if connected_time:
            duration = calculate_duration(transport['start_time'], connected_time)
            other_info = {
                "disconnect_time": disconnected_time,
                "failed_time": disconnected_time
            }
            transport_entry = {
                "direction": direction,
                "start_time": transport['start_time'],
                "end_time": connected_time,
                "duration": duration,
                "state": transport['connected_state'],
                "other_info": other_info
            }
            results['createTransport'].append(transport_entry)

    

    # 计算持续时间并打印结果
    for section in ['joinRoomInternal', 'queryRoom', 'join', 'verify_msg']:
        if 'start_time' in results[section] and results[section]['start_time'] and 'end_time' in results[section] and results[section]['end_time']:
            duration = calculate_duration(results[section]['start_time'], results[section]['end_time'])
            results[section]['duration'] = duration

    # 收集错误行
    for line in log_lines:
        if 'ERROR' in line:
            results['error_line'].append(line.strip())

    # 输出到文件
    with open(output_file_path, 'w') as output_file:
        output_file.write(json.dumps(results, indent=4))

    # 打印到控制台
    print(json.dumps(results, indent=4))

# 辅助函数：解析 JSON 数据
def parse_logs_detail_extract_json(log_lines, index):
    json_str = ''
    in_json = False
    for line in log_lines[index:]:
        if 'respData=' in line:
            json_str += line.split('=')[1].strip()
            in_json = True
        elif in_json:
            if line.startswith('}'):
                json_str += line.strip()
                break
            json_str += line.strip()
    return json_str