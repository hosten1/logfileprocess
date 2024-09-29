# -*- coding: utf-8 -*-
import argparse
import sys
import re
import os
import codecs
import json
import matplotlib

matplotlib.use("Agg")  # 切换到 Agg 后端
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime

# 定义全局常量
IMAGE_WIDTH_PIXELS = 1920
IMAGE_HEIGHT_PIXELS = 1080
DPI = 100
NATCH_SIZE = 99


class DataToPlot:
    # *5 是因为数据是1s一次 其他的图是6s一次
    def extract_and_plot_aslevels(
        self, log_file, out_path, batch_size=NATCH_SIZE * 5, callback=None
    ):
        if callback is None:
            # Provide a default callback that does nothing if not provided
            callback = lambda message: None
        """
        解析日志文件中的 ASLevels 数据，并将其分批次绘制成折线图。

        :param log_file: 日志文件路径
        :param batch_size: 每个子图显示的数据点数，默认 88
        """
        # 获取脚本所在目录并创建 logs 目录
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = out_path

        # 如果 logs 目录不存在，则创建它
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # 使用 codecs 打开文件，指定 utf-8 编码
        with codecs.open(log_file, "r", "utf-8", errors="ignore") as f:
            lines = f.readlines()

        aslevels_data = []

        # 正则表达式匹配包含 rtc_status 的行并捕获 { } 之间的 JSON 数据
        rtc_status_pattern = re.compile(r"rtc_status.*?(\{.*?\})")

        for line in lines:
            match = rtc_status_pattern.search(line)
            if match:
                json_str = match.group(1)
                try:
                    # 将匹配到的 JSON 字符串转换为 Python 字典
                    rtc_status_data = json.loads(json_str)

                    # 检查是否有 ASLevels 字段
                    if "ASLevels" in rtc_status_data:
                        levels_str = rtc_status_data["ASLevels"]
                        levels_values = [
                            float(value) for value in levels_str.split("|")
                        ]
                        aslevels_data.extend(levels_values)  # 合并所有 ASLevels 数据

                except ValueError:
                    # JSON 解析错误
                    print("Error decoding JSON on line: {}".format(line))

        # 输出合并后的 ASLevels 数据
        print("All Levels Data count: {}".format(aslevels_data))

        # 确认有数据可以绘制
        if aslevels_data:
            # 计算需要多少批次
            num_batches = (len(aslevels_data) // batch_size) + 1

            # 创建子图结构
            fig, axs = plt.subplots(
                num_batches,
                1,
                figsize=(
                    IMAGE_WIDTH_PIXELS / DPI,
                    (IMAGE_HEIGHT_PIXELS / DPI) * num_batches,
                ),
                dpi=DPI,
            )

            # 如果只有一个子图，则将 axs 转换为列表
            if num_batches == 1:
                axs = [axs]

            # 分批绘制 ASLevels 数据
            for i in range(num_batches):
                start_idx = i * batch_size
                end_idx = start_idx + batch_size

                # 绘制每个批次的数据
                axs[i].plot(
                    aslevels_data[start_idx:end_idx], label="ASLevels", marker="o"
                )

                axs[i].set_title("Batch {} - ASLevels over Time".format(i + 1))
                axs[i].set_xlabel("Data Point Index")
                axs[i].set_ylabel("Level Values")
                axs[i].legend()
                axs[i].grid(True)

            # 使用日志文件名作为图片名称，后缀为 _aslevels
            log_file_name = os.path.splitext(os.path.basename(log_file))[0]
            plot_filename = "{}_record_levels_aslevels.png".format(log_file_name)

            # 保存图像到 logs 目录
            plot_path = os.path.join(logs_dir, plot_filename)
            plt.tight_layout()  # 调整布局，避免子图重叠
            plt.savefig(plot_path)
            plt.close()

            print("ASLevels plot saved as '{}'".format(plot_path))
        else:
            print("No ASLevels data found.")

    # *5 是因为数据是1s一次 其他的图是6s一次
    def extract_and_plot_arlevels_recv(
        self, log_file, out_path, batch_size=NATCH_SIZE * 5, callback=None
    ):
        if callback is None:
            # Provide a default callback that does nothing if not provided
            callback = lambda message: None
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = out_path

        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        with codecs.open(log_file, "r", "utf-8", errors="ignore") as f:
            lines = f.readlines()

        peer_arlevels_data = {}
        recv_status_pattern = re.compile(r"recv status.*?(\{.*?\})")

        for line in lines:
            match = recv_status_pattern.search(line)
            if match:
                json_str = match.group(1)
                try:
                    recv_status_data = json.loads(json_str)
                    if "ARLevels" in recv_status_data and "peerID" in recv_status_data:
                        peer_id = recv_status_data["peerID"]
                        arlevels_str = recv_status_data["ARLevels"]
                        arlevels_values = [
                            float(value) for value in arlevels_str.split("|")
                        ]
                        if peer_id not in peer_arlevels_data:
                            peer_arlevels_data[peer_id] = []
                        peer_arlevels_data[peer_id].extend(arlevels_values)
                except ValueError:
                    print("Error decoding JSON on line: {}".format(line))

        for peer_id, arlevels_data in peer_arlevels_data.items():
            print(
                "All ARLevels for peerID {peer_id}: {arlevels_data}".format(
                    peer_id=peer_id, arlevels_data=arlevels_data
                )
            )

            if arlevels_data:
                num_batches = (len(arlevels_data) // batch_size) + 1
                fig, axs = plt.subplots(
                    num_batches,
                    1,
                    figsize=(
                        IMAGE_WIDTH_PIXELS / DPI,
                        (IMAGE_HEIGHT_PIXELS / DPI) * num_batches,
                    ),
                    dpi=DPI,
                )
                if num_batches == 1:
                    axs = [axs]

                for i in range(num_batches):
                    start_idx = i * batch_size
                    end_idx = start_idx + batch_size
                    axs[i].plot(
                        arlevels_data[start_idx:end_idx],
                        label="ARLevels for peerID {}".format(peer_id),
                    )
                    axs[i].set_xlabel("Data Points")
                    axs[i].set_ylabel("ARLevel Values")
                    axs[i].set_title("ARLevels - Batch {}".format(i + 1))
                    axs[i].legend()
                    axs[i].grid(True)

                log_file_name = os.path.splitext(os.path.basename(log_file))[0]
                plot_filename = "{}_arlevels_{}.png".format(log_file_name, peer_id)
                plot_path = os.path.join(logs_dir, plot_filename)
                plt.tight_layout()
                plt.savefig(plot_path)
                plt.close()
                print(
                    "ARLevels plot for peerID {} saved as '{}'".format(
                        peer_id, plot_path
                    )
                )

    def extract_and_plot_levels_RS(
        self, log_file, out_path, batch_size=NATCH_SIZE, callback=None
    ):
        if callback is None:
            # Provide a default callback that does nothing if not provided
            callback = lambda message: None
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        # logs_dir = os.path.join(script_dir, 'logs')
        logs_dir = out_path

        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        with codecs.open(log_file, "r", "utf-8", errors="ignore") as f:
            lines = f.readlines()

        aslevels_data = []
        peer_arlevels_data = {}

        rtc_status_pattern = re.compile(r"rtc_status.*?(\{.*?\})")
        recv_status_pattern = re.compile(r"recv status.*?(\{.*?\})")

        for line in lines:
            match_rtc = rtc_status_pattern.search(line)
            if match_rtc:
                json_str = match_rtc.group(1)
                try:
                    rtc_status_data = json.loads(json_str)
                    if "ASLevels" in rtc_status_data:
                        levels_str = rtc_status_data["ASLevels"]
                        levels_values = [
                            float(value) for value in levels_str.split("|")
                        ]
                        aslevels_data.extend(levels_values)
                        print("Current ASLevels Data: {}".format(levels_values))
                except ValueError:
                    print("Error decoding JSON on line: {}".format(line))

            match_recv = recv_status_pattern.search(line)
            if match_recv:
                json_str = match_recv.group(1)
                try:
                    recv_status_data = json.loads(json_str)
                    if "ARLevels" in recv_status_data and "peerID" in recv_status_data:
                        peer_id = recv_status_data["peerID"]
                        arlevels_str = recv_status_data["ARLevels"]
                        arlevels_values = [
                            float(value) for value in arlevels_str.split("|")
                        ]
                        if peer_id not in peer_arlevels_data:
                            peer_arlevels_data[peer_id] = []
                        peer_arlevels_data[peer_id].extend(arlevels_values)
                        print(
                            "Current ARLevels for peerID {peer_id}: {arlevels_values}".format(
                                peer_id=peer_id, arlevels_values=arlevels_values
                            )
                        )
                except ValueError:
                    print("Error decoding JSON on line: {}".format(line))

        # 绘制 ASLevels 数据
        if aslevels_data:
            num_batches = (len(aslevels_data) // batch_size) + 1
            fig, axs = plt.subplots(
                num_batches,
                1,
                figsize=(
                    IMAGE_WIDTH_PIXELS / DPI,
                    (IMAGE_HEIGHT_PIXELS / DPI) * num_batches,
                ),
                dpi=DPI,
            )
            if num_batches == 1:
                axs = [axs]

            for i in range(num_batches):
                start_idx = i * batch_size
                end_idx = start_idx + batch_size
                axs[i].plot(
                    aslevels_data[start_idx:end_idx],
                    label="send audio level",
                    color="blue",
                )

                # 在每个子图中绘制每个 peer 的 ARLevels
                for peer_id, arlevels_data in peer_arlevels_data.items():
                    if len(arlevels_data) > start_idx:
                        peer_arlevels_slice = arlevels_data[start_idx:end_idx]
                        axs[i].plot(
                            peer_arlevels_slice,
                            label="receive audio levels peer {}".format(peer_id),
                            linestyle="--",
                        )

                axs[i].set_xlabel("Data Points")
                axs[i].set_ylabel("Audio Level Values")
                axs[i].set_title("Audio Levels - Batch {}".format(i + 1))
                axs[i].legend()  # 添加图例
                axs[i].grid(True)

            # 保存图像
            log_file_name = os.path.splitext(os.path.basename(log_file))[0]
            plot_filename = "{}_combined_levels.png".format(log_file_name)
            plot_path = os.path.join(logs_dir, plot_filename)
            plt.tight_layout()
            plt.savefig(plot_path)
            plt.close()

            print("Combined ASLevels and ARLevels plot saved as '{}'".format(plot_path))

    def process_rtc_status_recv_data_logs(
        self,
        log_file_path,
        out_path,
        interval_s=6,
        batch_size=NATCH_SIZE,
        callback=None,
    ):
        if callback is None:
            # Provide a default callback that does nothing if not provided
            callback = lambda message: None
        """
        解析日志文件中的 rtc_status 行，提取 recvBytes、ARBitrate 和丢包率，并保存图表为文件。

        图片会保存到 logs 目录下，文件名与输入日志文件名一致，并附加 recv_other_data。

        :param log_file_path: 日志文件路径
        :param interval_s: 每条日志记录的时间间隔，默认 6 秒
        :param batch_size: 每次绘制多少个数据点，防止图表过于拥挤，默认 50
        """
        peer_data = defaultdict(
            lambda: {"recvBytes": [], "ARBitrate": [], "lossRate": []}
        )
        timestamps = []

        log_file_name = os.path.basename(log_file_path).replace(".log", "")
        try:
            with open(log_file_path, "r") as log_file:
                line_number = 0
                for line in log_file:
                    start_idx = line.find("{")
                    end_idx = line.rfind("}")

                    # 检查是否找到有效的 JSON 部分
                    if start_idx != -1 and end_idx != -1:
                        json_str = line[start_idx : end_idx + 1]
                        try:
                            data = json.loads(json_str)
                        except ValueError:  # 无法解析的行，跳过
                            continue

                        # 只处理符合条件的日志行
                        if data.get("direction") == "recv" and "peerID" in data:
                            peer_id = data["peerID"]

                            # 将 recvBytes 和 ARBitrate 转换成 KB
                            recv_bytes_kb = data["recvBytes"] / 1000.0
                            ar_bitrate_kb = data["ARBitrate"] / 1000.0

                            # 计算丢包率
                            ar_packets = data["ARPackets"]
                            ar_packets_lost = data["ARPacketsLost"]
                            if ar_packets + ar_packets_lost > 0:
                                loss_rate = ar_packets_lost / (
                                    ar_packets + ar_packets_lost
                                )
                            else:
                                loss_rate = 0

                            # 记录每个 peerID 下的数据
                            peer_data[peer_id]["recvBytes"].append(recv_bytes_kb)
                            peer_data[peer_id]["ARBitrate"].append(ar_bitrate_kb)
                            peer_data[peer_id]["lossRate"].append(loss_rate)

                            # 添加对应的时间戳
                            timestamps.append(line_number * interval_s)
                            line_number += 1

            for peer_id, data in peer_data.items():
                # 确保数据点一致性
                num_points = min(
                    len(data["recvBytes"]),
                    len(data["ARBitrate"]),
                    len(data["lossRate"]),
                )
                data["recvBytes"] = data["recvBytes"][:num_points]
                data["ARBitrate"] = data["ARBitrate"][:num_points]
                data["lossRate"] = data["lossRate"][:num_points]
                timestamps_batch = timestamps[:num_points]

                num_batches = (num_points // batch_size) + 1
                fig, axs = plt.subplots(
                    num_batches,
                    1,
                    figsize=(
                        IMAGE_WIDTH_PIXELS / DPI,
                        (IMAGE_HEIGHT_PIXELS / DPI) * num_batches,
                    ),
                    dpi=DPI,
                )
                if num_batches == 1:
                    axs = [axs]

                # 分批绘制图表
                for i in range(num_batches):
                    start_idx = i * batch_size
                    end_idx = min(start_idx + batch_size, num_points)

                    axs[i].plot(
                        timestamps_batch[start_idx:end_idx],
                        data["recvBytes"][start_idx:end_idx],
                        label="recvBytes (KB)",
                        marker="o",
                    )
                    axs[i].plot(
                        timestamps_batch[start_idx:end_idx],
                        data["ARBitrate"][start_idx:end_idx],
                        label="ARBitrate (KB)",
                        marker="s",
                    )
                    axs[i].plot(
                        timestamps_batch[start_idx:end_idx],
                        data["lossRate"][start_idx:end_idx],
                        label="Loss Rate",
                        marker="^",
                    )

                    axs[i].set_xlabel("Time (s)")
                    axs[i].set_ylabel("Value")
                    axs[i].set_title(
                        "PeerID: {} - Network Data (Batch {})".format(peer_id, i + 1)
                    )
                    axs[i].legend()
                    axs[i].grid(True)

                plt.tight_layout()
                # 保存图片到 logs 目录
                output_file_path = os.path.join(
                    out_path, "{}_recv_other_data_{}.png".format(log_file_name, peer_id)
                )
                plt.savefig(output_file_path)
                plt.close()
                print("图表已生成并保存到: {}".format(output_file_path))

        except IOError:
            print("日志文件未找到: {}".format(log_file_path))
        except Exception as e:
            print("发生错误: {}".format(str(e)))

    def process_rtc_status_send_data_logs(
        self,
        log_file_path,
        out_path,
        interval_s=6,
        batch_size=NATCH_SIZE,
        callback=None,
    ):
        if callback is None:
            # Provide a default callback that does nothing if not provided
            callback = lambda message: None
        """
        解析日志文件中的 rtc_status 行，提取 sendBytes、ASPacketsLost 和 rtt，并保存图表为文件。

        图片会保存到 logs 目录下，文件名与输入日志文件名一致，并附加 send_data。

        :param log_file_path: 日志文件路径
        :param interval_s: 每条日志记录的时间间隔，默认 6 秒
        :param batch_size: 每次绘制多少个数据点，防止图表过于拥挤，默认 50
        """
        send_data = {"sendBytes": [], "lossRate": [], "rtt": []}
        timestamps = []
        print("开始处理日志文件: {}".format(log_file_path))
        log_file_name = os.path.basename(log_file_path).replace(".log", "")
        try:
            with open(log_file_path, "r") as log_file:
                line_number = 0
                for line in log_file:
                    if "rtc_status:" in line:
                        start_idx = line.find("{")
                        end_idx = line.rfind("}")

                        # 检查是否找到有效的 JSON 部分
                        if start_idx != -1 and end_idx != -1:
                            json_str = line[start_idx : end_idx + 1]
                            try:
                                data = json.loads(json_str)
                            except ValueError:  # 无法解析的行，跳过
                                continue

                            # 只处理符合条件的日志行
                            if data.get("direction") == "send":
                                # 提取 sendBytes、ASPackets 和 ASPacketsLost
                                send_bytes = (
                                    data.get("sendBytes", 0) / 1000.0
                                )  # 转换成 KB
                                as_packets = data.get("ASPackets", 0)
                                as_packets_lost = data.get("ASPacketsLost", 0)
                                rtt = data.get("rtt", 0)

                                # 计算丢包率
                                if as_packets + as_packets_lost > 0:
                                    loss_rate = as_packets_lost / (
                                        as_packets + as_packets_lost
                                    )
                                else:
                                    loss_rate = 0

                                # 记录数据
                                send_data["sendBytes"].append(send_bytes)
                                send_data["lossRate"].append(loss_rate)
                                send_data["rtt"].append(rtt)

                                # 添加对应的时间戳
                                timestamps.append(line_number * interval_s)
                                line_number += 1

            # 确保数据点一致性
            num_points = min(
                len(send_data["sendBytes"]),
                len(send_data["lossRate"]),
                len(send_data["rtt"]),
            )
            send_data["sendBytes"] = send_data["sendBytes"][:num_points]
            send_data["lossRate"] = send_data["lossRate"][:num_points]
            send_data["rtt"] = send_data["rtt"][:num_points]
            timestamps_batch = timestamps[:num_points]

            num_batches = (num_points // batch_size) + 1
            fig, axs = plt.subplots(
                num_batches,
                1,
                figsize=(
                    IMAGE_WIDTH_PIXELS / DPI,
                    (IMAGE_HEIGHT_PIXELS / DPI) * num_batches,
                ),
                dpi=DPI,
            )
            if num_batches == 1:
                axs = [axs]

            # 分批绘制图表
            for i in range(num_batches):
                start_idx = i * batch_size
                end_idx = min(start_idx + batch_size, num_points)

                axs[i].plot(
                    timestamps_batch[start_idx:end_idx],
                    send_data["sendBytes"][start_idx:end_idx],
                    label="sendBytes (KB)",
                    marker="o",
                )
                axs[i].plot(
                    timestamps_batch[start_idx:end_idx],
                    send_data["lossRate"][start_idx:end_idx],
                    label="Loss Rate",
                    marker="s",
                )
                axs[i].plot(
                    timestamps_batch[start_idx:end_idx],
                    send_data["rtt"][start_idx:end_idx],
                    label="RTT (ms)",
                    marker="^",
                )

                axs[i].set_xlabel("Time (s)")
                axs[i].set_ylabel("Value")
                axs[i].set_title("Send Data (Batch {})".format(i + 1))
                axs[i].legend()
                axs[i].grid(True)

            plt.tight_layout()

            # 保存图片到 logs 目录
            output_file_path = os.path.join(
                out_path, "{}_send_data.png".format(log_file_name)
            )
            plt.savefig(output_file_path)
            plt.close()
            print("图表已生成并保存到: {}".format(output_file_path))

        except IOError:
            print("日志文件未找到: {}".format(log_file_path))
        except Exception as e:
            print("发生错误: {}".format(str(e)))
