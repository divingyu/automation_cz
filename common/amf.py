"""
Company            :
Create Date        : 2025-01-24 14:25:03
Engineer           : You Yuling
Target Devices     : amf
Tool Versions      : v_1.0
Description        : amf method
Revision           : LastEditTime
"""
import os
import re
import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import paramiko

from common.sshserver import Serv


class AmfServ(Serv):
    def __init__(self, cfg_amf_data, label: str = 'AMF'):
        self.ax = None
        self.fig = None
        try:
            self.exec_path = cfg_amf_data['exec_path']
            self.log_path = cfg_amf_data['log_path']
            super().__init__(cfg_amf_data['amf_ip'], cfg_amf_data['amf_user'], cfg_amf_data['amf_pwd'],
                             cfg_amf_data['amf_port'])
            self.iperf_ports = set()
            self.rate_file = ''
            self.label = label
            self.times = np.array([])
            self.rates = np.array([])
        except Exception:
            raise KeyError(f"file configuration error, please check config.json configuration file : {self.label} CFG")

    def capture_pcap(self, label2: str = '0'):
        current_datetime = datetime.now()
        date_format = '%Y-%m-%d_%H_%M_%S'
        formatted_date = current_datetime.strftime(date_format)
        print(f"\nStarting capture tcpdump in Amf. {self.label} host:{self.target_host}")
        cmd = f'cd {self.log_path}; nohup tcpdump -i any -w {self.label}_{formatted_date}_{label2}.pcap > /dev/null ' \
              f'2>&1 &'
        try:
            self.exec_server_cmd(cmd, False)
        except paramiko.SSHException as ssh_ex:
            print(f"execuate capture pcap fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")

    def clean_log_trace(self):
        cmd = f'cd {self.log_path}; rm -rf *'
        print(f"Cleaning AMF log and trace files... {self.label} Host:{self.target_host}")
        try:
            self.exec_server_cmd(cmd, False)
        except paramiko.SSHException as ssh_ex:
            print(f"Clean cmd fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")

    def download_log(self, remote_directory: str):
        print(f'Downloading amf log. {self.label} Host:{self.target_host}')
        current_datetime = datetime.now()
        date_format = '%Y-%m-%d_%H_%M_%S'
        formatted_date = current_datetime.strftime(date_format)
        remote_directory = f'{remote_directory}\\{self.label}_{formatted_date}'
        if not os.path.exists(remote_directory):
            os.mkdir(remote_directory)
        sftp_client = self.target_ssh_client.get_transport().open_sftp_client()
        for filename in sftp_client.listdir(f'{self.log_path}'):
            filepath = f'{self.log_path}/{filename}'
            print(f'downloading {self.label} file:{filepath}')
            sftp_client.get(filepath, f'{remote_directory}\\{filename}')
        if not os.listdir(remote_directory):
            os.rmdir(remote_directory)
        print(f'AMF log download completed. {self.label} Host:{self.target_host}')

    def kill_iperf_com(self):
        if self.iperf_cmd != '':
            iperf_filed = re.search(r'iperf.*-([cs])', self.iperf_cmd).group(1)
            iperf_port = re.search(r'.*-p\s+(\d+)', self.iperf_cmd).group(1)
            self.iperf_ports.add(iperf_port)
            iperf_cmd = f'ps -ef | grep "iperf.*-{iperf_filed}.*-p.*{iperf_port}" | grep -v "grep"'
            stdin, stdout, stderr = self.target_ssh_client.exec_command(iperf_cmd)
            for line in stdout.readlines():
                if line != '':
                    pid = line.split()[1]
                    kill_cmd = f'kill -9 {pid}'
                    stdin, stdout, stderr = self.target_ssh_client.exec_command(kill_cmd)
                    stdout.read().decode()

    def kill_iperf(self):
        if self.iperf_cmd != '':
            iperf_port_str = '|'.join(str(port) for port in self.iperf_ports)
            # print(f"AMF {iperf_port_str}")
            iperf_cmd = f'ps -ef | grep -E "iperf.*({iperf_port_str})" | grep -v "grep"'
            stdin, stdout, stderr = self.target_ssh_client.exec_command(iperf_cmd)
            for line in stdout.readlines():
                if line != '':
                    pid = line.split()[1]
                    kill_cmd = f'kill -9 {pid}'
                    stdin, stdout, stderr = self.target_ssh_client.exec_command(kill_cmd)
                    stdout.read().decode()

    def execute_udp_client(self, ue_ip, bw_size, length: int = 1300, during_time: int = 9999, port: int = 5001):
        self.iperf_cmd = f'nohup iperf -u -c {ue_ip} -B {self.target_host} -b {bw_size} -i 1 -l {length} -t ' \
                         f'{during_time} -p {port} > /dev/null 2>&1 &'
        self.kill_iperf_com()
        print(f"Beginning to perform DL traffic.  {self.label} Host:{self.target_host}...")
        print(f"DL CMD : {self.iperf_cmd}")
        stdin, stdout, stderr = self.target_ssh_client.exec_command(self.iperf_cmd)
        channel = stdout.channel
        if channel is not None:
            try:
                if channel.recv_ready():
                    channel.recv(1024)
            except paramiko.SSHException as ssh_ex:
                print(f"UDP Client execute fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")
        else:
            print(f"UDP Client Channel is None. Command execution failed.  {self.label} Host:{self.target_host}")

    def execute_udp_server(self, filename: str = 'ul_udp.txt', port: int = 5001):
        self.rate_file = filename
        self.iperf_cmd = f'cd {self.log_path}; nohup iperf -u -s -i 1 -B {self.target_host} -p {port} > ' \
                         f'{self.rate_file} &'
        self.kill_iperf_com()
        print(f"SERVER CMD : {self.iperf_cmd} {self.label} Host:{self.target_host}")
        stdin, stdout, stderr = self.target_ssh_client.exec_command(self.iperf_cmd)
        channel = stdout.channel
        if channel is not None:
            try:
                if channel.recv_ready():
                    channel.recv(1024)
            except paramiko.SSHException as ssh_ex:
                print(f"UDP Server execute fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")
        else:
            print(f"UDP Server Channel is None. Command execution failed.  {self.label} Host:{self.target_host}")

    def show_udp_rate(self):
        show_cmd = f"cd {self.log_path}; tail -f {self.rate_file}"
        stdin, stdout, stderr = self.target_ssh_client.exec_command(show_cmd)
        channel = stdout.channel
        try:
            while not stdout.channel.eof_received:
                if channel.recv_ready():
                    output = channel.recv(1024).decode('utf-8')
                    print(output, end = '')
                elif channel.exit_status_ready():
                    break
                time.sleep(0.01)
        except KeyboardInterrupt:
            print('Exiting...')

    def show_udp_rate_plt(self):
        plt.ion()
        self.fig, self.ax = plt.subplots()
        show_cmd = f"cd {self.log_path}; tail -f {self.rate_file}"
        stdin, stdout, stderr = self.target_ssh_client.exec_command(show_cmd)
        channel = stdout.channel
        time_num = 0
        try:
            while not stdout.channel.eof_received:
                if channel.recv_ready():
                    output = channel.recv(1024).decode('utf-8')
                    rates_mbps = re.findall(r'([\d.]+)\s+Mbits/sec', output)
                    if not rates_mbps:
                        rates_kbps = re.findall(r'([\d.]+)\s+Kbits/sec', output)
                        if not rates_kbps:
                            rates_mbps = 0
                        else:
                            rates_mbps = float(rates_kbps[0]) / 1000
                    else:
                        rates_mbps = float(rates_mbps[0])
                    self.update_rate(time_num, rates_mbps)
                    time_num += 1
                    print(output, end = '')
                elif channel.exit_status_ready():
                    break
                time.sleep(0.01)
        except KeyboardInterrupt:
            print('Exiting...')
        finally:
            plt.ioff()

    def update_rate(self, time_num, rate):
        self.times = np.append(self.times, time_num)
        self.rates = np.append(self.rates, rate)
        y_max = self.rates.max()
        self.ax.clear()
        plt.ylim(0, y_max + 100)
        plt.plot(self.times, self.rates, label = 'Rate/Mpbs')
        plt.title(self.rate_file)
        plt.xlabel("time/s", loc = 'right')
        plt.legend(loc = 'upper left')
        self.fig.tight_layout()
        plt.draw()
        plt.pause(0.1)
