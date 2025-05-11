"""
Company            :
Create Date        : 2025-01-08 09:12:02
Engineer           : You Yuling
Target Devices     : ssh server
Tool Versions      : v_1.0
Description        : autotest
Revision           : LastEditTime
"""
import paramiko


class Serv:
    ue_ip = ''
    iperf_cmd = ''
    ssh_client = ''
    ssh_jump = ''

    def __init__(self, target_host, target_user, target_password, target_port: int = 22):
        self.target_host = target_host
        self.target_user = target_user
        self.target_password = target_password
        self.target_port = target_port
        self.jump_host = ''
        self.jump_user = ''
        self.jump_password = ''
        self.jump_port = 22
        self.target_ssh_client = None

    def closed_ssh(self):
        if self.target_ssh_client:
            self.target_ssh_client.close()
            print(f"Release {self.target_host} !!!")
        if self.ssh_jump:
            self.ssh_jump.close()
            print(f"Release {self.jump_host} !!!")
        if self.ssh_client:
            self.ssh_client.close()

    def kill_tcpdump(self):
        print(f"\nStarting kill capture tcpdump, host:{self.target_host}")
        cmd = "source /etc/profile > /dev/null;ps -ef | grep tcpdump | grep -v grep | awk '{print $2}' | xargs -I {} " \
              "kill --SIGINT {}"
        try:
            self.exec_server_cmd(cmd, False)
        except paramiko.SSHException as ssh_ex:
            print(f"execuate kill tcpdump fail! Error: {ssh_ex} on: {self.target_host}")

    def connect_jump_sever(self, cfg_jump_data):
        self.jump_host = cfg_jump_data['jump_ip']
        self.jump_user = cfg_jump_data["jump_user"]
        self.jump_password = cfg_jump_data['jump_pwd']
        self.jump_port = cfg_jump_data['jump_port']
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=self.jump_host, username=self.jump_user, password=self.jump_password, port=self.jump_port)
            self.ssh_jump = self.ssh_client.get_transport().open_channel(
                'direct-tcpip', (self.target_host, self.target_port), (self.jump_host, self.jump_port))
            print(f"Successful connection of springboard machine:{self.jump_host}")
        except paramiko.SSHException as ssh_ex:
            print(f"Failed to establish jump SSH connection {ssh_ex} :: {self.jump_host}")
            return None

    def connet_target_sever(self):
        try:
            self.target_ssh_client = paramiko.SSHClient()
            self.target_ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.ssh_jump:
                self.target_ssh_client.connect(
                    hostname=self.target_host, username=self.target_user, password=self.target_password,
                    port=self.target_port, sock=self.ssh_jump)
                print(f"the Host({self.target_host}) Connection Successful")
            else:
                self.target_ssh_client.connect(
                    hostname=self.target_host, username=self.target_user, password=self.target_password,
                    port=self.target_port)
                print(f"the Host({self.target_host}) Connection Successful")
            return self.target_ssh_client
        except paramiko.ssh_exception.SSHException as ssh_ex:
            raise RuntimeError(f"ssh connect timeout: {ssh_ex}")
        except paramiko.ssh_exception.NoValidConnectionsError as nvce:
            raise RuntimeError(f"unable to establish a valid connection: {nvce}")

    def exec_server_cmd(self, cmd: str, is_print=True) -> str:
        if is_print:
            print(f"Executing command: {cmd} on Host: {self.target_host}")
        try:
            stdin, stdout, stderr = self.target_ssh_client.exec_command(cmd)
            channel = stdout.channel
            output = []
            while not channel.exit_status_ready() or channel.recv_ready():
                if channel.recv_ready():
                    output.append(channel.recv(1024).decode('utf-8'))
            return ''.join(output)
        except paramiko.SSHException as ssh_ex:
            print(f"Failed to execute command: {cmd}. Error: {ssh_ex} on Host: {self.target_host}")
            return ""


if __name__ == '__main__':
    pass
