import re
import sys
import os
import fnmatch
import matplotlib.pyplot as plt
from multiprocessing import Process

file_matches = []


def find_files(directory, pattern):
    root_depth = directory.count(os.sep)
    for root, dirs, files in os.walk(directory):
        current_depth = root.count(os.sep) - root_depth
        if current_depth > 3:
            # 超过指定深度，不再继续递归
            dirs[:] = []  # 清空 dirs 列表，防止 os.walk() 继续遍历子目录
            continue
        for filename in fnmatch.filter(files, pattern):
            file_matches.append(os.path.join(root, filename))
    return file_matches


def obtain_rates(filename: str, pattern: str) -> list:
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()
    rates = []
    for line in lines:
        # [  3]  0.0- 1.0 sec  57.2 MBytes   480 Mbits/sec   0.032 ms   16/46152 (0.035%)
        iperf_udp = re.match(r"\[\s+\d+\]\s+.*?Bytes.*", line)
        if iperf_udp is None:
            continue
        # print(iperf_udp.group(0))
        columns = re.search(pattern, iperf_udp.group(0))
        if columns is None:
            rates.append(0)
            continue
        # print(columns.group(1))
        else:
            rates.append(round(float(columns.group(1)), 3))
    return rates


def plot_rate_and_packetloss_graph(
    rates: list, packet_loss: list, filename: str = "UDP Traffic"
):
    x = [i for i in range(len(rates))]
    # plt.ion()
    fig, ax1 = plt.subplots()
    # 绘制第一组数据（速度）
    color = "tab:blue"
    ax1.set_xlim(0, len(x) + 10)
    ax1.set_xlabel("time/s", loc="right")
    ax1.set_ylim(0, max(rates) + 100)
    # ax1.set_ylabel('Rate/Mpbs', color=color,loc='top',rotation=360)
    ax1.plot(x, rates, color=color, label="Rate/Mpbs")
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.legend(loc="upper left")
    # 创建第二个y轴，共享同一个x轴
    ax2 = ax1.twinx()
    color = "tab:orange"
    ax2.set_ylim(0, max(packet_loss) + 10)
    # ax2.set_ylabel('packet loss/%', color=color, loc='top', rotation=360)
    ax2.plot(x, packet_loss, color=color, label="packet loss/%")
    ax2.tick_params(axis="y", labelcolor=color)
    ax2.legend(loc="upper right")
    plt.title(filename)
    fig.tight_layout()
    plt.show()
    # plt.draw()
    # plt.pause(0.1)


def plot_rate_graph(rates: list, filename: str = "UDP Traffic"):
    x = [i for i in range(len(rates))]
    plt.ion()
    plt.xlim(0, len(x) + 100)
    plt.ylim(0, max(rates) + 200)
    plt.plot(x, rates, label="Rate/Mpbs")
    plt.title(filename)
    plt.xlabel("time/s", loc="right")
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.draw()
    plt.pause(0.1)


if __name__ == "__main__":
    ps = []
    if len(sys.argv) < 2:
        print("Usage: python3 plotrate.py [filename*]")
        exit()
    for filenames in sys.argv[1:]:
        dir = os.path.dirname(filenames)
        if dir == "":
            dir = "."
        base = os.path.basename(filenames)
        find_files(dir, base)
    if len(file_matches) == 0:
        print("No file matches the pattern.")
    for filename in file_matches:
        if os.path.isfile(filename) and os.access(filename, os.R_OK):
            y1 = obtain_rates(filename, r"([\d\.]+)\s+Mbits/sec")
            y2 = obtain_rates(filename, r"\(([\d\.]+)%\)")
            # plot_rate_and_packetloss_graph(y1,y2,filename)
            filename = os.path.basename(filename)
            p = Process(
                target=plot_rate_and_packetloss_graph,
                args=(
                    y1,
                    y2,
                    filename,
                ),
            )
            ps.append(p)
        else:
            print(f"{filename} is not a file, does not exist, or is not readable.")
    for p in ps:
        p.start()
    for p in ps:
        p.join()
    # plt.pause(100)
