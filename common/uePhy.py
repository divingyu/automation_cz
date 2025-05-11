"""
Company            :
Create Date        : 2025-01-24 14:20:21
Engineer           : You Yuling
Target Devices     : ue phy
Tool Versions      : v_1.0
Description        : ue phy method
Revision           : LastEditTime
"""
import os
import time
import paramiko
from datetime import datetime
from common.sshserver import Serv


def telnet_recv(recv_obj: paramiko.channel.Channel):
    output = []
    while recv_obj.recv_ready():
        output.append(recv_obj.recv(1024).decode('utf-8'))
        time.sleep(0.01)
    return ''.join(output)


class UePhyServ(Serv):

    def __init__(self, cfg_ue_phy_data, label: str = 'UePhy'):
        try:
            self.exec_path = cfg_ue_phy_data['exec_path']
            self.log_path = cfg_ue_phy_data['log_path']
            self.label = label
            self.__shell_phy = None
            super().__init__(cfg_ue_phy_data['ue_ip'], cfg_ue_phy_data['ue_user'], cfg_ue_phy_data['ue_pwd'],
                             cfg_ue_phy_data['ue_port'])
        except Exception:
            raise KeyError(f"file configuration error, please check config.json configuration file : {self.label} CFG")

    def clean_log_trace(self):
        cmd = f'cd {self.log_path}; rm -rf *'
        print(f"Cleaning UE PHY log and trace files... {self.label} Host:{self.target_host}")
        try:
            self.exec_server_cmd(cmd, False)
        except paramiko.SSHException as ssh_ex:
            print(f"Clean cmd fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")

    def upload_file(self, local_file: str, remote_file_path: str):
        print(f"Uploading file. {self.label} Host:{self.target_host}")
        self.exec_server_cmd(f'cd {remote_file_path} && rm -rf *', is_print=False)
        remote_file = f'{remote_file_path}/{os.path.basename(local_file)}'
        sftp_client = self.target_ssh_client.get_transport().open_sftp_client()
        sftp_client.put(local_file, remote_file)
        self.exec_server_cmd(f'cd {remote_file_path} && tar -zxvf {remote_file}', is_print=False)
        self.exec_server_cmd(f'rm -rf {remote_file} && cd {remote_file.split(".")[0]} && mv ./* ../', is_print=False)
        self.exec_server_cmd(f'cd {remote_file_path} && sync', is_print=False)
        print(f"File upload and uncompress completed. {self.label} Host:{self.target_host}")

    def attach_ue(self):
        attach_cmd = f'export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin;cd ' \
                     f'{self.exec_path};./start.sh > /dev/null 2>&1 &'
        print(f"Starting up the ue phy, {self.label} Host:{self.target_host}")
        try:
            self.exec_server_cmd(attach_cmd, False)
        except paramiko.SSHException as ssh_ex:
            print(f"./start.sh execuate fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")

    def release_ue(self):
        print(f"Starting stop the ue phy {self.label} Host{self.target_host}")
        stop_cmd = f'export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/' \
                   f'sbin:/bin;cd {self.exec_path};nohup ./stop.sh > /dev/null 2>&1 &'
        try:
            self.exec_server_cmd(stop_cmd, False)
        except paramiko.SSHException as ssh_ex:
            print(f"./stop.sh execuate fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")

    def download_log(self, remote_directory):
        print(f'Downloading UE PHY log. {self.label} Host:{self.target_host}')
        current_datetime = datetime.now()
        date_format = '%Y-%m-%d_%H_%M_%S'
        formatted_date = current_datetime.strftime(date_format)
        remote_directory = f'{remote_directory}\\{self.label}_{formatted_date}'
        if not os.path.exists(remote_directory):
            os.mkdir(remote_directory)
        cmd = f"cd {self.log_path};" \
              "find . -name '*.txt' -size +20000k -exec tar -czvf ue_phy.tar.gz {} \\; -exec rm -rf {} \\;"
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
        sftp_client = self.target_ssh_client.get_transport().open_sftp_client()
        for filename in sftp_client.listdir(f'{self.log_path}'):
            filepath = f'{self.log_path}/{filename}'
            print(f'downloading {self.label} file:{filepath}')
            sftp_client.get(filepath, f'{remote_directory}\\{filename}')
        print(f'UE PHY log download completed. {self.label} Host:{self.target_host}')

    def telnet_PHY(self, timeout: int = 30):
        current_time = datetime.now().timestamp()
        self.__shell_phy = self.target_ssh_client.invoke_shell()
        while not self.__shell_phy.recv_ready():
            time.sleep(1)
        self.__shell_phy.send('telnet 127.0.0.1 9000\n')
        while True:
            if self.__shell_phy.recv_ready():
                output = self.__shell_phy.recv(1024).decode()
                if 'Username:' in output:
                    self.__shell_phy.send('czlh\n')
                elif 'Password:' in output:
                    self.__shell_phy.send('innogence\n')
                elif 'IG OMC>' in output:
                    self.__shell_phy.send('telnet PHY\n')
                    break
            time.sleep(1)
            nowtime = datetime.now().timestamp()
            if nowtime - current_time > timeout:
                raise RuntimeError(f"Ue telnet PHY start failed! {self.label} Host: {self.target_host}")
        time.sleep(1)
        telnet_recv(self.__shell_phy)
        print(f"telnet PHY success! {self.label} Host:{self.target_host}")
        return self.__shell_phy

    def execuate_phy_cmd(self, cmd: str, delay: int = 1) -> str:
        if self.__shell_phy is None:
            print(f"UE PHY not connected, trying to connect...{self.label} Host:{self.target_host}")
            self.telnet_PHY()
        self.__shell_phy.send(f'{cmd}\n')
        time.sleep(delay)
        return telnet_recv(self.__shell_phy)
