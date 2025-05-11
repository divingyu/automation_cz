"""
Company            :
Create Date        : 2025-01-24 14:30:58
Engineer           : You Yuling
Target Devices     : remote PC
Tool Versions      : v_1.0
Description        : remote PC operator
Revision           : LastEditTime
"""
import paramiko
from datetime import datetime
from common.sshserver import Serv


class PcServ(Serv):
    def __init__(self, cfg_pc_data, label: str = 'PC'):
        try:
            self.label = label
            self.pcap_file = ''
            super().__init__(cfg_pc_data['jump_ip'], cfg_pc_data['jump_user'], cfg_pc_data['jump_pwd'],
                             cfg_pc_data['jump_port'])
        except Exception:
            raise KeyError(f"file configuration error, please check config.json configuration file : {self.label} CFG")

    def capture_pcap(self, label: str = '', pcap_choice: int = 0, interface: int = 6):
        current_datetime = datetime.now()
        date_format = '%Y-%m-%d_%H_%M_%S'
        formatted_date = current_datetime.strftime(date_format)
        pcap_tools = ['tshark', 'dumpcap']
        print(f"\nStarting capture pcap in Remote Pc. host:{self.target_host}")
        if label != '':
            self.pcap_file = f'{formatted_date}_{label}.pcap'
        else:
            self.pcap_file = f'{formatted_date}.pcap'
        cmd = f'{pcap_tools[pcap_choice]} -i {interface} -f "port 54122" -w {self.pcap_file}'
        stdin, stdout, stderr = self.target_ssh_client.exec_command(cmd)
        channel = stdout.channel
        if channel.recv_ready():
            channel.recv(1024).decode('cp936')

    def stop_pcap(self, local_directory: str, pcap_choice: int = 0):
        try:
            print(f"\nStarting stop capture pcap in Remote Pc. host:{self.target_host}")
            pcap_tools = ['tshark', 'dumpcap']
            pid = self.exec_server_cmd(f'tasklist | findstr {pcap_tools[pcap_choice]}', is_print=False)
            pid = pid.split()[1]
            self.exec_server_cmd(f'taskkill /pid {pid} /f', is_print=False)
            pwd = self.exec_server_cmd('chdir', is_print=False)
            sftp_client = self.target_ssh_client.get_transport().open_sftp_client()
            remote_file_path = f'{pwd.strip()}\\{self.pcap_file}'
            local_file_path = f'{local_directory}\\{self.pcap_file}'
            sftp_client.get(remote_file_path, local_file_path)
            self.exec_server_cmd(f'del {self.pcap_file}', is_print=False)
        except IndexError:
            print(f"not check pcap process in Remote Pc. host:{self.target_host}")
        except OSError:
            print(f"not check pcap file in Remote Pc. host:{self.target_host}")

    def exec_server_cmd(self, cmd: str, is_print=True) -> str:
        if is_print:
            print(f"exec cmd: {cmd}  Host:{self.target_host}")
        stdin, stdout, stderr = self.target_ssh_client.exec_command(cmd)
        channel = stdout.channel
        output_str = ''
        try:
            while not channel.eof_received:
                if channel.recv_ready():
                    output = channel.recv(1024).decode('cp936')
                    output_str += output
            return output_str
        except paramiko.SSHException as ssh_ex:
            print(f"execuate cmd fail! Error: {ssh_ex} on {self.target_host}")
