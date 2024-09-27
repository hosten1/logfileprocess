# -*- coding: utf-8 -*-
import re
import codecs
import os
import json
from datetime import datetime


class details_logs:
    def search_joinRoom_end_(self, file_all_log_lines, results, callback):
        # 寻找 joinRoomInternalWithDisplayName(end) 行
        callback("找 joinRoomInternalWithDisplayName(end) 行")
        time_pattern = r"\[(\d{2}:\d{2}:\d{2}:\d{3})"
        line_cout = 0
        for next_line in file_all_log_lines:
            if "joinRoomInternalWithDisplayName(end)" in next_line:
                callback("joinRoomInternalWithDisplayName(end) found.")
                server_info_match = re.search(
                    r"serverInfo:(http[s]?://[^ ]+)", next_line
                )
                if server_info_match:
                    server_addr = server_info_match.group(1)
                    results["joinRoomInternal"]["server_ip"] = str(server_addr)

                #
                # 匹配 这样的行到 appInfo：{"version": "1.0", "name": "MyApp"
                app_info_match_first = re.search(r"appInfo：(\{.*)", next_line)
                if app_info_match_first:
                    app_info_match_str = app_info_match_first.group(1)

                    # 当前行的下一行 这里得判断当前是不是最后一行如果是就不应该继续取下一行
                    next_line_str = None
                    if line_cout + 1 < len(file_all_log_lines):
                        next_line_str = file_all_log_lines[line_cout + 1]

                    # 如果下一行没有时间戳，则跳过
                    if next_line_str and not re.match(
                        time_pattern, next_line_str
                    ):  # 修改点
                        # 匹配一次 '"version": "1.0", "name": "MyApp"} and some other info' 表示json结束
                        app_info_match = re.search(r"(.+?})", next_line)
                        if app_info_match:
                            app_info = app_info_match.group(
                                1
                            )  # 获取到包括 } 在内的内容
                            app_info_match_str += str(app_info)
                            app_info_match_str = (
                                app_info_match_str.replace("=", ":")
                                .replace("(", "[")
                                .replace(")", "]")
                            )
                            callback("app_info: {}".format(app_info_match_str))
                            results["joinRoomInternal"]["app_info"] = str(
                                app_info_match_str
                            )
                            break
                        else:
                            app_info_match_str += next_line_str

                        continue
                    else:
                        app_info_match = re.search(r"appInfo：(\{.*\})", next_line)
                        app_info = app_info_match_first.group(1)
                        # 处理 app_info
                        app_info = (
                            app_info.replace("=", ":")
                            .replace("(", "[")
                            .replace(")", "]")
                        )
                        app_info = json.loads(app_info)
                        results["joinRoomInternal"]["app_info"] = str(app_info)
                        break

            else:
                err = ""
                # callback("No joinRoomInternalWithDisplayName(end) found.")

            # Step 2: 查找 _protoo Peer "open" event
        callback('查找 _protoo Peer "open" event')
        for log_line in file_all_log_lines:
            # 正则表达式
            pattern = r'protoo Peer.*?".*?open'
            # 匹配
            match = re.search(pattern, log_line)

            if match:
                callback(" protoo Peer 'open' event found.")
                open_time_match = re.search(time_pattern, log_line)
                if open_time_match:
                    callback(
                        " protoo Peer 'open' event found open_time_match={}. ".format(
                            open_time_match.group(1)
                        )
                    )
                    results["joinRoomInternal"]["end_time"] = open_time_match.group(1)
                    break
                else:
                    callback(
                        " protoo Peer 'open' event found. open_time_match not found."
                    )

                # else:
                # callback("No protoo Peer 'open' event found.")
            line_cout += 1

    # 分析socketio发送数据相关  开始
    def extract_json_from_logs_(self, log_lines):
        extracted_logs = []  # 存储提取出来的日志
        for i, line in enumerate(log_lines):
            if "sendMessage" in line:
                # 找到包含 sendMessage 的行
                print("找到日志行: {}".format(line))

                before_json_part = line.split("{")[0].strip()  # 提取 { 之前的内容
                json_lines = []  # 存储 JSON 部分的行
                # //如果一行有完整的 直接处理
                if line.find("{") != -1 and re.search(r"}\s*(array|method)?", line):
                    print("找到日志行: {}".format(line))
                    # 将结果存储为字典并添加到数组
                    extracted_logs.append(
                        {"before_json": line, "json": "", "after_json": ""}
                    )
                    continue
                # 找到 JSON 开始的部分
                json_start_index = line.find("{")
                if json_start_index != -1:
                    json_lines.append(line[json_start_index:].strip())

                    # 标志 JSON 开始
                    json_started = True
                    after_json_part = ""  # 初始化 JSON 之后的部分
                    for j in range(i + 1, len(log_lines)):
                        current_line = log_lines[j].strip()

                        if json_started:
                            # 检查 JSON 是否结束
                            if re.search(r"}\s*(array|method)?", current_line):
                                # JSON 部分结束，分割行内容
                                json_end_split = current_line.split("}", 1)
                                json_lines.append(
                                    json_end_split[0] + "}"
                                )  # 保留 } 作为 JSON 的一部分
                                after_json_part = (
                                    json_end_split[1].strip()
                                    if len(json_end_split) > 1
                                    else ""
                                )
                                break
                            else:
                                json_lines.append(current_line)

                # 拼接所有 JSON 行为一个完整的字符串
                full_json_str = " ".join(json_lines)

                # 将结果存储为字典并添加到数组
                extracted_logs.append(
                    {
                        "before_json": before_json_part,
                        "json": full_json_str,
                        "after_json": after_json_part,
                    }
                )

        return extracted_logs

    def analyze_logs_from_file(self, log_file_path):
        with codecs.open(log_file_path, "r", "utf-8") as log_file:
            log_lines = log_file.readlines()

        extracted_logs = self.extract_json_from_logs_(log_lines)

        output_filename = "{}_analyze_process.log".format(
            os.path.splitext(log_file_path)[0]
        )

        if not os.path.exists("logs"):
            os.makedirs("logs")

        with codecs.open(output_filename, "w", "utf-8") as f:
            for log in extracted_logs:
                f.write("Before JSON: {}\n".format(log["before_json"]))
                f.write("Extracted JSON: {}\n".format(log["json"]))
                f.write("After JSON: {}\n".format(log["after_json"]))
                f.write("---------------------------\n")

        print("日志分析结果已保存到: {}".format(output_filename))

    # 分析socketio发送数据相关  结束

    def parse_logs_detail(
        self,
        input_file_path,
        out_file_pth,
        output_file_name="output_results.json",
        callback=None,
    ):
        if callback is None:
            # Provide a default callback that does nothing if not provided
            callback = lambda message: None
        # 确保 logs 目录存在
        logs_dir = out_file_pth
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        def get_output_file_path(input_file_path, logs_dir):
            # 提取输入文件名和扩展名
            file_name, file_extension = os.path.splitext(
                os.path.basename(input_file_path)
            )

            # 构造输出文件名，添加 'output_results'
            output_file_name = f"{file_name}_output_results{file_extension}"

            # 设置输出文件路径
            output_file_path = os.path.join(logs_dir, output_file_name)

            return output_file_path

        # 设置输出文件路径
        output_file_path = get_output_file_path(input_file_path, out_file_pth)
        callback("Starting analysis output_file_path = {}...".format(output_file_path))

        results = {
            "createTransport": [],
            "join": {},
            "verify_msg": {},
            "queryRoom": {},
            "joinRoomInternal": {},
            "error_line": [],
        }

        time_pattern = r"\[(\d{2}:\d{2}:\d{2}:\d{3})"

        file_all_log_lines = []
        # 读取日志文件
        with open(input_file_path, "r") as input_file:
            file_all_log_lines = input_file.readlines()

        # Step 1: 处理 joinRoomInternal
        for line in file_all_log_lines:
            if "joinRoomInternalWithDisplayName(begin)" in line:
                # 匹配第一个开始的日志时间 19:15:17:547
                start_time_match = re.search(time_pattern, line)
                join_room_internal_start_time = None
                if start_time_match:
                    # 如果匹配到，则提取时间
                    join_room_internal_start_time = start_time_match.group(1)
                    results["joinRoomInternal"][
                        "start_time"
                    ] = join_room_internal_start_time

                    callback(
                        "joinRoomInternal start_time: {}".format(
                            join_room_internal_start_time
                        )
                    )

                self.search_joinRoom_end_(file_all_log_lines, results, callback)
                break

        # Step 3: 查找 Verify msg:
        callback("Searching for Verify msg:")
        for line in file_all_log_lines:
            if "Verify msg:" in line:
                verify_time_match = re.search(time_pattern, line)
                if verify_time_match:
                    results["verify_msg"] = {
                        "verify_time": verify_time_match.group(1),
                        "end_time": "",
                        "duration": 0,
                    }
                    callback(
                        "Verify msg success: {}".format(
                            results["verify_msg"]["verify_time"]
                        )
                    )
                break

        # Step 4: 处理 queryRoom
        callback("Searching for queryRoom:")
        for idx, line in enumerate(file_all_log_lines):
            if "sending mediasoup request [method:queryRoom]" in line:
                query_room_start_time_match = re.search(time_pattern, line)
                if query_room_start_time_match:
                    results["queryRoom"]["start_time"] = (
                        query_room_start_time_match.group(1)
                    )
                    callback(
                        "queryRoom start_time: {}".format(
                            results["queryRoom"]["start_time"]
                        )
                    )

                    continue
                    # 查找对应的 callback
            if (
                "sendMessage(method = queryRoom)" in line
                and "callback:respData" in line
            ):
                query_room_end_time_match = re.search(time_pattern, line)
                if query_room_end_time_match:
                    results["queryRoom"]["end_time"] = query_room_end_time_match.group(
                        1
                    )
                callback(
                    "Searching for queryRoom callback success end_time={}".format(
                        results["queryRoom"]["end_time"]
                    )
                )
                break

        # Step 5: 处理 join
        callback("Searching for join:")
        for idx, line in enumerate(file_all_log_lines):
            if "sending mediasoup request [method:join]" in line:
                join_start_time_match = re.search(time_pattern, line)
                if join_start_time_match:
                    results["join"]["start_time"] = join_start_time_match.group(1)
                    callback(
                        "join start_time: {}".format(results["join"]["start_time"])
                    )
                    continue

            # 查找对应的 callback 并提取 JSON 数据
            if "callback:respData" in line and "join" in line:
                join_end_time_match = re.search(time_pattern, line)
                if join_end_time_match:
                    results["join"]["end_time"] = join_end_time_match.group(1)
                    # json_str = self.parse_logs_detail_extract_json(
                    #     file_all_log_lines, idx
                    # )
                    # json_str = (
                    #     json_str.replace("=", ":").replace("(", "[").replace(")", "]")
                    # )
                    # results["join"]["resp_data"] = json.loads(json_str)
                    callback(
                        "Searching for join callback success end_time={}".format(
                            results["join"]["end_time"]
                        )
                    )
                    break

        # Step 6: 处理 createTransport
        transports = {}

        # 处理 createTransport
        for line in file_all_log_lines:
            if "createTransport()" in line:
                direction_match = re.search(r"direction:\((\w+)\)", line)
                if direction_match:
                    direction = direction_match.group(1)
                    start_time_match = re.search(time_pattern, line)
                    if start_time_match:
                        start_time = start_time_match.group(1)
                        transport_entry = {
                            "direction": direction,
                            "start_time": start_time,
                            "connected_time": "",
                            "connected_state": "",
                            "disconnected_time": "",
                            "disconnected_state": "",
                        }
                        transports[direction] = transport_entry

        # 收集每个方向的事件
        for line in file_all_log_lines:
            if "Transport connection state changed to" in line:
                direction_match = re.search(r"direction:\s*(\w+)", line)
                if direction_match:
                    direction = direction_match.group(1)
                    if direction in transports:
                        state_time_match = re.search(time_pattern, line)
                        if state_time_match:
                            state = re.search(
                                r"Transport connection state changed to\s+(\w+)", line
                            ).group(1)
                            state_time = state_time_match.group(1)
                            if state == "connected":
                                transports[direction]["connected_time"] = state_time
                                transports[direction]["connected_state"] = state
                            else:
                                transports[direction]["disconnected_time"] = state_time
                                transports[direction]["disconnected_state"] = state

        # 计算每个事件的持续时间
        def calculate_duration(sestart_time, end_time):
            start = map(int, start_time.split(":"))
            end = map(int, end_time.split(":"))
            start_ms = sum([x * y for x, y in zip(start, [3600000, 60000, 1000, 1])])
            end_ms = sum([x * y for x, y in zip(end, [3600000, 60000, 1000, 1])])
            return end_ms - start_ms

        # 组织结果
        for direction, transport in transports.items():
            connected_time = transport["connected_time"]
            disconnected_time = transport["disconnected_time"]

            if connected_time:
                duration = calculate_duration(transport["start_time"], connected_time)
                other_info = {
                    "disconnect_time": disconnected_time,
                    "failed_time": disconnected_time,
                }
                transport_entry = {
                    "direction": direction,
                    "start_time": transport["start_time"],
                    "end_time": connected_time,
                    "duration": duration,
                    "state": transport["connected_state"],
                    "other_info": other_info,
                }
                results["createTransport"].append(transport_entry)

        # 计算持续时间并打印结果
        for section in ["joinRoomInternal", "queryRoom", "join", "verify_msg"]:
            if (
                "start_time" in results[section]
                and results[section]["start_time"]
                and "end_time" in results[section]
                and results[section]["end_time"]
            ):
                duration = calculate_duration(
                    results[section]["start_time"], results[section]["end_time"]
                )
                results[section]["duration"] = duration

        # 收集错误行
        for line in file_all_log_lines:
            if "ERROR" in line:
                results["error_line"].append(line.strip())

        # 输出到文件
        with open(output_file_path, "w") as output_file:
            output_file.write(json.dumps(results, indent=4))

        # 打印到控制台
        print(json.dumps(results, indent=4))

    # 辅助函数：解析 JSON 数据
    def parse_logs_detail_extract_json(self, log_lines, index):
        json_str = ""
        in_json = False
        for line in log_lines[index:]:
            if "respData=" in line:
                json_str += line.split("=")[1].strip()
                in_json = True
            elif in_json:
                if line.startswith("}"):
                    json_str += line.strip()
                    break
                json_str += line.strip()
        return json_str
