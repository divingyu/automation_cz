"""
Company            :
Create Date        : 2025-01-24 14:07:18
Engineer           : You Yuling
Target Devices     : ue_mac
Tool Versions      : v_1.0
Description        : ue mac method
Revision           : LastEditTime
"""
import os
import re
import time
import paramiko
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from common.sshserver import Serv


def telnet_recv(recv_obj: paramiko.channel.Channel):
    output = []
    while recv_obj.recv_ready():
        output.append(recv_obj.recv(1024).decode('utf-8'))
        time.sleep(0.01)
    return ''.join(output)


class UeMacServ(Serv):
    def __init__(self, cfg_ue_mac_data, label: str = 'ueMac'):
        self.ax = None
        self.fig = None
        try:
            self.exec_path = cfg_ue_mac_data['exec_path']
            self.log_path = cfg_ue_mac_data['log_path']
            super().__init__(cfg_ue_mac_data['ue_ip'], cfg_ue_mac_data['ue_user'], cfg_ue_mac_data['ue_pwd'],
                             cfg_ue_mac_data['ue_port'])
            self.rate_file = ''
            self.iperf_ports = set()
            self.ue_ip = ''
            self.label = label
            self.times = np.array([])
            self.rates = np.array([])
            self.__shell_mac = None
        except Exception:
            raise KeyError(f"file configuration error, please check config.json configuration file : {self.label} CFG")

    def clean_log_trace(self):
        cmd = f'cd {self.log_path}; rm -rf *'
        print(f"Cleaning UE MAC log and trace. {self.label} Host:{self.target_host}")
        try:
            self.exec_server_cmd(cmd, False)
        except paramiko.SSHException as ssh_ex:
            print(f"Clean cmd fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")

    def upload_file(self, local_file: str, remote_file_path: str):
        print(f"Uploading file. {self.label} Host:{self.target_host}")
        remote_file = f'{remote_file_path}/{os.path.basename(local_file)}'
        sftp_client = self.target_ssh_client.get_transport().open_sftp_client()
        sftp_client.put(local_file, remote_file)
        self.exec_server_cmd(f'cd {remote_file_path} && tar -zxvf {remote_file}', is_print=False)
        self.exec_server_cmd(f'rm -rf {remote_file} && cd {remote_file.split(".")[0]} && chmod -R +x *', is_print=False)
        self.exec_server_cmd(f'cd {remote_file_path} && chmod 755 {remote_file.split(".")[0]}', is_print=False)
        self.exec_path = remote_file.split('.')[0]
        print(f"File upload and uncompress completed. {self.label} Host:{self.target_host}")

    def capture_pcap(self, label2: str = '0'):
        current_datetime = datetime.now()
        date_format = '%Y-%m-%d_%H_%M_%S'
        formatted_date = current_datetime.strftime(date_format)
        print(f"\nStarting capture tcpdump in Ue. {self.label} host:{self.target_host}")
        cmd = f'cd {self.log_path}; nohup tcpdump -i any -w {self.label}_{formatted_date}_{label2}.pcap > /dev/null ' \
              f'2>&1 &'
        try:
            self.exec_server_cmd(cmd, False)
        except paramiko.SSHException as ssh_ex:
            print(f"execuate capture pcap fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")

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
            iperf_cmd = f'ps -ef | grep -E "iperf.*({iperf_port_str})" | grep -v "grep"'
            stdin, stdout, stderr = self.target_ssh_client.exec_command(iperf_cmd)
            for line in stdout.readlines():
                if line != '':
                    pid = line.split()[1]
                    kill_cmd = f'kill -9 {pid}'
                    stdin, stdout, stderr = self.target_ssh_client.exec_command(kill_cmd)
                    stdout.read().decode()

    def execuate_udp_client(self, target_host, bw_size, during_time: int = 9999, port: int = 5001):
        self.iperf_cmd = f'nohup taskset -c 4 iperf -u -c {target_host} -b {bw_size} -i 1 -l 1300 -t {during_time}' \
                         f' -p {port} > /dev/null 2>&1 &'
        self.kill_iperf_com()
        print(f"Beginning to perform UL traffic. {self.label} Host:{self.target_host}...")
        stdin, stdout, stderr = self.target_ssh_client.exec_command(self.iperf_cmd)
        channel = stdout.channel
        if channel is not None:
            try:
                if channel.recv_ready():
                    channel.recv(1024)
            except paramiko.SSHException as ssh_ex:
                print(f"UDP Client execuate fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")
        else:
            print(f"UDP Client Channel is None. Command execution failed.  {self.label}:{self.target_host}")

    def execuate_udp_server(self, filename: str = "dl_udp.txt", port: int = 5001):
        self.rate_file = filename
        self.iperf_cmd = f'cd {self.log_path}; nohup iperf -s -u -i 1 -p {port} > {self.rate_file} &'
        self.kill_iperf_com()
        stdin, stdout, stderr = self.target_ssh_client.exec_command(self.iperf_cmd)
        channel = stdout.channel
        if channel is not None:
            try:
                if channel.recv_ready():
                    channel.recv(1024)
            except paramiko.SSHException as ssh_ex:
                print(f"UDP Server execuate fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")
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
                    # print(rate)
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

    def download_log(self, remote_directory: str):
        print(f'Downloading UE MAC log. {self.label} Host:{self.target_host}')
        current_datetime = datetime.now()
        date_format = '%Y-%m-%d_%H_%M_%S'
        formatted_date = current_datetime.strftime(date_format)
        remote_directory = f'{remote_directory}\\{self.label}_{formatted_date}'
        cmd = f"cd {self.log_path};" \
              "find . -maxdepth 1 -type f -name 'uel2_*' -size +1k -print0 |xargs -0 ls -t | head -n 3 | awk -F / '{" \
              "print $2}' | xargs tar -czvf ueMacl2.tar.gz;" \
              "find . -maxdepth 1 -type f -name 'uel3_*' -size +1k -print0 |xargs -0 ls -t | head -n 3 | awk -F / '{" \
              "print $2}' | xargs tar -czvf ueMacl3.tar.gz;" \
              "find . -maxdepth 1 -type f -name 'user-tti*' -size +1k -print0 |xargs -0 ls -t | head -n 3 | awk -F / " \
              "'{print $2}' | xargs tar -czvf ueMacTti.tar.gz;" \
              "find . -maxdepth 1 -type f -name '*.pcap' -print0 |xargs -0 tar -czvf pcap.tar.gz;"
        stdin, stdout, stderr = self.target_ssh_client.exec_command(cmd)
        channel = stdout.channel
        progress = ""
        try:
            while not channel.eof_received:
                if channel.recv_ready():
                    channel.recv(1024).decode('utf-8')
                    progress += "***"
                    time.sleep(1)
                    print(f"\rDownloading check {self.label} log:{progress}", end = '')
                elif channel.exit_status_ready():
                    break
        except paramiko.SSHException as ssh_ex:
            print(f"execuate compress fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")
        print('')
        if self.rate_file != '':
            ue_mac_file_list = [f'{self.rate_file}', 'uel2.log', 'uel3.log', 'ueom.log', 'ueMacl2.tar.gz',
                                'ueMacl3.tar.gz', 'ueMacTti.tar.gz', 'pcap.tar.gz']
        else:
            ue_mac_file_list = ['uel2.log', 'uel3.log', 'ueom.log', 'ueMacl2.tar.gz', 'ueMacl3.tar.gz',
                                'ueMacTti.tar.gz', 'pcap.tar.gz']
        if not os.path.exists(remote_directory):
            os.mkdir(remote_directory)
        sftp_client = self.target_ssh_client.get_transport().open_sftp_client()
        for filename in ue_mac_file_list:
            filepath = f'{self.log_path}/{filename}'
            try:
                print(f'downloading {self.label} file:{filepath}')
                sftp_client.get(filepath, f'{remote_directory}\\{filename}')
            except (IOError, FileNotFoundError):
                print(f"File '{filepath}' does not exist on the remote server. {self.label} Host:{self.target_host}")
                if os.path.exists(f'{remote_directory}\\{filename}'):
                    os.remove(f'{remote_directory}\\{filename}')
        cmd = f'cd {self.log_path}; rm -rf *.tar.gz *.pcap'
        self.exec_server_cmd(cmd, False)
        print(f'UE MAC log download completed. {self.label} Host:{self.target_host}')

    def attach_ue(self, timeout: int = 60):
        if self.ue_ip != '':
            print(f"UE ip has been obtained. ue ip:{self.ue_ip}; {self.label} Host:{self.target_host}")
        else:
            attach_cmd = f'source /etc/profile > /dev/null;cd {self.exec_path};nohup ./igus.sh > /dev/null 2>&1 &'
            print(f"Starting up the ue mac, {self.label} Host:{self.target_host}")
            try:
                self.exec_server_cmd(attach_cmd, False)
            except paramiko.SSHException as ssh_ex:
                print(f"./igus.sh execuate fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")
            self.check_ue_whether_attach(timeout)

    def check_ue_whether_attach(self, timeout: int = 60):
        start_timestamp = datetime.now().timestamp()
        print(f'*******({self.target_host})Detecting ue ip***********')
        progress = ''
        while True:
            if self.obtain_ue_ip() == '':
                progress += "***"
                print(f"\r[{progress}]", end = '')
                time.sleep(5)
                current_timestamp = datetime.now().timestamp()
                if current_timestamp - start_timestamp >= timeout:
                    raise RuntimeError(f"No ue ip detected!! timeout={timeout}; {self.label}: {self.target_host}")
            else:
                break

    def release_ue(self):
        print(f"Starting stop the ue mac. {self.label} Host:{self.target_host}")
        attach_cmd = f'source /etc/profile > /dev/null;cd {self.exec_path};nohup ./kill.sh > /dev/null 2>&1 &'
        try:
            self.exec_server_cmd(attach_cmd, False)
        except paramiko.SSHException as ssh_ex:
            print(f"./kill.sh execuate fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")

    def obtain_ue_ip(self):
        cmd = 'ip -4 addr'
        stdin, stdout, stderr = self.target_ssh_client.exec_command(cmd)
        output = stdout.read().decode()
        ip_filed = re.search(r'inet\s+((\d+\.){3}\d+).*ige', output)
        if ip_filed:
            self.ue_ip = ip_filed.group(1)
            print(f'\nThe UE IP address has been obtained: {self.ue_ip}, {self.label} Host:{self.target_host}')
            return self.ue_ip
        else:
            return ''

    def telnet_mac(self, timeout: int = 30):
        current_time = datetime.now().timestamp()
        self.__shell_mac = self.target_ssh_client.invoke_shell()
        while not self.__shell_mac.recv_ready():
            time.sleep(1)
        self.__shell_mac.send('telnet 127.0.0.1 9010\n')
        while True:
            if self.__shell_mac.recv_ready():
                output = self.__shell_mac.recv(1024).decode()
                if 'Username:' in output:
                    self.__shell_mac.send('admin\r')
                elif 'Password:' in output:
                    self.__shell_mac.send('123\r')
                    break
            time.sleep(1)
            nowtime = datetime.now().timestamp()
            if nowtime - current_time > timeout:
                raise RuntimeError(f"Ue telnet Mac start failed! {self.label} Host: {self.target_host}")
        time.sleep(1)
        telnet_recv(self.__shell_mac)
        print(f"telnet UE mac success! {self.label} Host:{self.target_host}")
        return self.__shell_mac

    def execuate_mac_cmd(self, cmd: str, delay: int = 1) -> str:
        if self.__shell_mac is None:
            print(f"UE mac not connected, trying to connect...{self.label} Host:{self.target_host}")
            self.telnet_mac()
        self.__shell_mac.send(f'{cmd}\r')
        time.sleep(delay)
        return telnet_recv(self.__shell_mac)
