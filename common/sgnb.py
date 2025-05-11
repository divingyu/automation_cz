"""
Company            :
Create Date        : 2025-01-24 13:57:00
Engineer           : You Yuling
Target Devices     : Sgnb
Tool Versions      : v_1.0
Description        : Sgnb module
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


class SgnbServ(Serv):
    def __init__(self, cfg_sgnb_data, label: str = 'Sgnb'):
        try:
            self.exec_path = cfg_sgnb_data['exec_path']
            self.log_path = cfg_sgnb_data['log_path']
            self.__shell_l3 = None
            self.__shell_scf = None
            self.label = label
            super().__init__(cfg_sgnb_data['sgnb_ip'], cfg_sgnb_data['sgnb_user'], cfg_sgnb_data['sgnb_pwd'],
                             cfg_sgnb_data['sgnb_port'])
        except Exception:
            raise KeyError(f"file configuration error, please check config.json configuration file : {self.label} CFG")

    def clean_log_trace(self):
        clean_sgnb = f"cd {self.log_path}; rm -rf *"
        clean_omc = "cd /var/log/inno/bbu; rm -rf *"
        try:
            self.exec_server_cmd(clean_sgnb, is_print=False)
            self.exec_server_cmd(clean_omc, is_print=False)
        except paramiko.SSHException as ssh_ex:
            print(f"Clean cmd fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")

    def upload_cfg_file(self, local_file: str, remote_file: str):
        print(f"Uploading file. {self.label} Host:{self.target_host}")
        try:
            sftp_client = self.target_ssh_client.get_transport().open_sftp_client()
        except paramiko.ssh_exception.SSHException:
            cmd = f"mkdir -p /usr/lib/openssh;ln -s /usr/local/libexec/sftp-server /usr/lib/openssh/sftp-server"
            self.exec_server_cmd(cmd, is_print=False)
            sftp_client = self.target_ssh_client.get_transport().open_sftp_client()
        sftp_client.put(local_file, remote_file)

    def upload_file(self, local_file: str, remote_file_path: str):
        print(f"Uploading file. {self.label} Host:{self.target_host}")
        remote_file = f"{remote_file_path}/{os.path.basename(local_file)}"
        try:
            sftp_client = self.target_ssh_client.get_transport().open_sftp_client()
        except paramiko.ssh_exception.SSHException:
            cmd = f"mkdir -p /usr/lib/openssh;ln -s /usr/local/libexec/sftp-server /usr/lib/openssh/sftp-server"
            self.exec_server_cmd(cmd, is_print=False)
            sftp_client = self.target_ssh_client.get_transport().open_sftp_client()
        sftp_client.put(local_file, remote_file)
        self.exec_server_cmd(
            f"cd {remote_file_path} && tar -zxvf {remote_file}", is_print=False
        )
        self.exec_server_cmd(
            f"rm -rf {remote_file} && cd {remote_file.split('.')[0]} && chmod -R +x *",
            is_print=False,
        )
        self.exec_path = remote_file.split(".")[0]
        print(
            f"File upload and uncompress completed. {self.label} Host:{self.target_host}"
        )

    def update_bsp(self, local_bsp_file: str):
        try:
            sftp_client = self.target_ssh_client.get_transport().open_sftp_client()
        except paramiko.ssh_exception.SSHException:
            cmd = f"mkdir -p /usr/lib/openssh;ln -s /usr/local/libexec/sftp-server /usr/lib/openssh/sftp-server"
            self.exec_server_cmd(cmd, is_print=False)
            sftp_client = self.target_ssh_client.get_transport().open_sftp_client()
        bsp_file = os.path.basename(local_bsp_file)
        bsp_serv_path = f"/root/boot/{bsp_file}"
        print(f"update the BSP file {bsp_file}")
        self.exec_server_cmd(f"cp {bsp_serv_path} {bsp_serv_path}.bak", is_print=False)
        sftp_client.put(local_bsp_file, f"{bsp_serv_path}")
        self.exec_server_cmd(f"chmod 777 {bsp_serv_path}", is_print=False)
        self.exec_server_cmd("sync", is_print=False)

    def download_log(self, remote_directory: str):
        print(f"Downloading Sgnb log. {self.label} Host:{self.target_host}")
        current_datetime = datetime.now()
        date_format = "%Y-%m-%d_%H_%M_%S"
        formatted_date = current_datetime.strftime(date_format)
        remote_directory = f"{remote_directory}\\{self.label}_{formatted_date}"
        cmd = (
            f"source /etc/profile > /dev/null;cd {self.log_path}/l2_TTI/;"
            "find . -maxdepth 1 -type f -name 'ttitrace_*' -size +10k -print0 |xargs -0 ls -t | head -n 3 | "
            "awk -F / '{print $2}' | xargs tar -czvf ../sgnb_tti_l2.tar.gz;"
            f"cd {self.log_path} && tar -czvf l1.tar.gz l1/*;"
            f"cd {self.log_path};"
            "find . -maxdepth 1 -type f -name '*.pcap' -print0 |xargs -0 tar -czvf sgnb_pcap.tar.gz;"
            f"mkdir -p {self.log_path}/om && cp /var/log/inno/bbu/* -r {self.log_path}/om;"
            f"cd {self.log_path} && tar -czvf om.tar.gz om/*"
        )
        stdin, stdout, stderr = self.target_ssh_client.exec_command(cmd)
        channel = stdout.channel
        progress = ""
        try:
            while not channel.eof_received:
                if channel.recv_ready():
                    channel.recv(1024).decode("utf-8")
                    progress += "***"
                    time.sleep(1)
                    print(f"\rDownloading check {self.label} log:{progress}", end="")
                elif channel.exit_status_ready():
                    break
        except paramiko.SSHException as ssh_ex:
            print(f"execuate compress fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")
        print("")
        sgnb_file_list = [
            "l2.log",
            "l3.log",
            "om.tar.gz",
            "sgnb_tti_l2.tar.gz",
            "l1.tar.gz",
            "sgnb_pcap.tar.gz",
            "start.txt",
        ]
        if not os.path.exists(remote_directory):
            os.mkdir(remote_directory)
        try:
            sftp_client = self.target_ssh_client.get_transport().open_sftp_client()
        except paramiko.ssh_exception.SSHException:
            cmd = f"mkdir -p /usr/lib/openssh;ln -s /usr/local/libexec/sftp-server /usr/lib/openssh/sftp-server"
            stdin, stdout, stderr = self.target_ssh_client.exec_command(cmd)
            channel = stdout.channel
            if channel.recv_ready():
                channel.recv(1024)
            sftp_client = self.target_ssh_client.get_transport().open_sftp_client()

        for filename in sgnb_file_list:
            filepath = f"{self.log_path}/{filename}"
            try:
                print(f"downloading {self.label} file:{filepath}")
                sftp_client.get(filepath, f"{remote_directory}\\{filename}")
            except (IOError, FileNotFoundError):
                print(
                    f"File '{filepath}' does not exist on the remote server. {self.label} Host:{self.target_host}"
                )
                if os.path.exists(f"{remote_directory}\\{filename}"):
                    os.remove(f"{remote_directory}\\{filename}")
        cmd = f"cd {self.log_path}; rm -rf *.tar.gz *.pcap"
        self.exec_server_cmd(cmd)
        print(f"Sgnb log download completed. host:{self.target_host}")

    def start_sgnb_processAndScf(self, timeout: int = 60):
        current_time = datetime.now().timestamp()
        cmd = f'source /etc/profile > /dev/null;cd {self.exec_path};sh start_dub.sh'
        print(f"Starting SGNB process. {self.label} host:{self.target_host}")
        self.__shell_scf = self.target_ssh_client.invoke_shell()
        while not self.__shell_scf.recv_ready():
            time.sleep(1)
        self.__shell_scf.send(f'{cmd}\n')
        count = 0
        while True:
            output = self.__shell_scf.recv(1024).decode()
            print(output)
            if 'recv from ip' in output:
                count += 1
            if count >= 6:
                break
            time.sleep(1)
            nowtime = datetime.now().timestamp()
            if nowtime - current_time > timeout:
                raise RuntimeError(f"Sgnb Scf start failed! {self.label} Host: {self.target_host}")

    def execuate_scf_cmd(self, cmd: str, delay: int = 1) -> str:
        if self.__shell_scf is None:
            print(f"No scf is running, please run it manually.{self.label} Host:{self.target_host}")
            return ''
        self.__shell_scf.send(f'{cmd}\n')
        time.sleep(delay)
        return telnet_recv(self.__shell_scf)

    def start_sgnb_process(self, new_architecture=True, is_copy_cfg=False):
        if new_architecture:
            cmd = f"source /etc/profile > /dev/null;cd {self.exec_path};nohup sh start_dub.sh -f 3.8G > " \
                  "/dev/null 2>&1 &"
            print(
                f"Starting SGNB new architecture process. {self.label} host:{self.target_host}"
            )
            self.exec_server_cmd(cmd, is_print=False)
            copy_cmd = (
                f"cp {self.exec_path}/etc/configs/data/data.xml /var/data/config/"
            )
            if is_copy_cfg:
                print(
                    f"Copying SGNB data.xml file to /var/data/config/. {self.label} host:{self.target_host}"
                )
                self.exec_server_cmd(copy_cmd, is_copy_cfg)
        else:
            cmd = f"source /etc/profile > /dev/null;cd {self.exec_path};nohup sh start_dub.sh -f 3.8G -o > " \
                  "/dev/null 2>&1 &"
            print(
                f"Starting SGNB old architecture process. {self.label} host:{self.target_host}"
            )
            self.exec_server_cmd(cmd, is_print=False)
            copy_cmd = (
                f"cp {self.exec_path}/etc/configs/nr_cfg_Data.xml /var/data/config/"
            )
            if is_copy_cfg:
                print(
                    f"Copying SGNB nr_cfg_Data.xml file to /var/data/config/. {self.label} host:{self.target_host}"
                )
                self.exec_server_cmd(copy_cmd, is_copy_cfg)

    def stop_sgnb_process(self):
        cmd = f'source /etc/profile > /dev/null;cd {self.exec_path}; ./kill.sh'
        print(f"Stopping SGNB process. Sgnb host:{self.target_host}")
        stdin, stdout, stderr = self.target_ssh_client.exec_command(cmd)
        channel = stdout.channel
        try:
            while not channel.eof_received:
                if channel.recv_ready():
                    channel.recv(1024)
                elif channel.exit_status_ready():
                    break
            print(f"the SGNB process stop completed. {self.label} host:{self.target_host}")
        except paramiko.SSHException as ssh_ex:
            print(f"execuate stop cmd fail! Error: {ssh_ex} on {self.label}:{self.target_host}")

    def start_sgnb_scf(self, timeout: int = 60):
        current_time = datetime.now().timestamp()
        cmd = f'source /etc/profile > /dev/null;cd {self.exec_path}/usr/scf; ./SCF_TEST'
        print(f"Starting SGNB SCF process. {self.label} Host:{self.target_host}")
        self.__shell_scf = self.target_ssh_client.invoke_shell()
        while not self.__shell_scf.recv_ready():
            time.sleep(1)
        self.__shell_scf.send(f'{cmd}\n')
        count = 0
        while True:
            output = self.__shell_scf.recv(1024).decode()
            print(output, end="")
            if 'recv from ip' in output:
                count += 1
            if count >= 6:
                break
            time.sleep(1)
            nowtime = datetime.now().timestamp()
            if int(nowtime - current_time) > timeout:
                raise RuntimeError(f"Sgnb Scf start failed! {self.label} Host: {self.target_host}")

    def capture_pcap(self, label2: str = '0'):
        current_datetime = datetime.now()
        date_format = '%Y-%m-%d_%H_%M_%S'
        formatted_date = current_datetime.strftime(date_format)
        print(f"\nStarting capture tcpdump in Sgnb. {self.label} host:{self.target_host}")
        cmd = f'source /etc/profile > /dev/null;cd {self.log_path};nohup tcpdump -i any -w {self.label}_"\
              "{formatted_date}_{label2}.pcap > /dev/null 2>&1 &'
        try:
            self.exec_server_cmd(cmd, is_print=False)
        except paramiko.SSHException as ssh_ex:
            print(f"execuate capture pcap fail! Error: {ssh_ex} on {self.label} Host:{self.target_host}")

    def telnet_L3(self, timeout: int = 30):
        current_time = datetime.now().timestamp()
        self.__shell_l3 = self.target_ssh_client.invoke_shell()
        while not self.__shell_l3.recv_ready():
            time.sleep(1)
        self.__shell_l3.send('telnet 127.0.0.1 9000\n')
        while True:
            if self.__shell_l3.recv_ready():
                output = self.__shell_l3.recv(1024).decode()
                if 'Username:' in output:
                    self.__shell_l3.send('czlh\n')
                elif 'Password:' in output:
                    self.__shell_l3.send('innogence\n')
                elif 'IG OMC>' in output:
                    self.__shell_l3.send('telnet L3\n')
                    break
            time.sleep(1)
            nowtime = datetime.now().timestamp()
            if nowtime - current_time > timeout:
                raise RuntimeError(f"Sgnb telnet L3 start failed! {self.label} Host: {self.target_host}")
        time.sleep(1)
        telnet_recv(self.__shell_l3)
        print(f"telnet L3 success! {self.label} Host:{self.target_host}")
        return self.__shell_l3

    def execuate_l3_cmd(self, cmd: str, delay: int = 1) -> str:
        if self.__shell_l3 is None:
            print(f"L3 not connected, trying to connect...{self.label} Host:{self.target_host}")
            self.telnet_L3()
        self.__shell_l3.send(f'{cmd}\n')
        time.sleep(delay)
        result = telnet_recv(self.__shell_l3)
        if "Idle timeout" in result:
            print(f"L3 idle, trying to connect...{self.label} Host:{self.target_host}")
            self.telnet_L3()
            self.__shell_l3.send(f"{cmd}\n")
            time.sleep(delay)
            result = telnet_recv(self.__shell_l3)
        return result

    def telnet_L2(self, cpu_id: str = '0x20', timeout: int = 30):
        """
        Connect to a specific CPU via telnet L2 using the given CPU ID.
        :param cpu_id: The CPU identifier (e.g., '0x20', '0x21', etc.)
        :param timeout: Timeout for the connection attempt
        """
        current_time = datetime.now().timestamp()
        shell_l2 = self.target_ssh_client.invoke_shell()
        while not shell_l2.recv_ready():
            time.sleep(1)
        shell_l2.send('telnet 127.0.0.1 9000\n')
        while True:
            if shell_l2.recv_ready():
                output = shell_l2.recv(1024).decode()
                if 'Username:' in output:
                    shell_l2.send('czlh\n')
                elif 'Password:' in output:
                    shell_l2.send('innogence\n')
                elif 'IG OMC>' in output:
                    shell_l2.send(f'telnet L2 {cpu_id}\n')
                    break
            time.sleep(1)
            nowtime = datetime.now().timestamp()
            if nowtime - current_time > timeout:
                raise RuntimeError(
                    f"Sgnb telnet L2 to cpu {cpu_id} start failed! {self.label} Host: {self.target_host}")
        time.sleep(1)
        telnet_recv(shell_l2)
        print(f"telnet L2 to cpu {cpu_id} success! {self.label} Host:{self.target_host}")
        return shell_l2

    def execuate_l2_cmd(self, shell_l2: str, cmd: str, cpu_id: str = '0x20', delay: int = 1) -> str:
        if shell_l2 is None:
            print(f"L2 to cpu {cpu_id} not connected, trying to connect...{self.label} Host:{self.target_host}")
            shell_l2 = self.telnet_L2(cpu_id)
        shell_l2.send(f'{cmd}\n')
        time.sleep(delay)
        result = telnet_recv(shell_l2)
        if "Idle timeout" in result:
            print(f"L2 to cpu {cpu_id} idle, trying to connect...{self.label} Host:{self.target_host}")
            shell_l2 = self.telnet_L2(cpu_id)
            shell_l2.send(f"{cmd}\n")
            time.sleep(delay)
            result = telnet_recv(shell_l2)
        return result

    def telnet_PHY(self, cpu_id: str = '0x20', timeout: int = 30):
        current_time = datetime.now().timestamp()
        shell_phy = self.target_ssh_client.invoke_shell()
        while not shell_phy.recv_ready():
            time.sleep(1)
        shell_phy.send('telnet 127.0.0.1 9000\n')
        while True:
            if shell_phy.recv_ready():
                output = shell_phy.recv(1024).decode()
                if 'Username:' in output:
                    shell_phy.send('czlh\n')
                elif 'Password:' in output:
                    shell_phy.send('innogence\n')
                elif 'IG OMC>' in output:
                    shell_phy.send(f'telnet PHY {cpu_id}\n')
                    break
            time.sleep(1)
            nowtime = datetime.now().timestamp()
            if nowtime - current_time > timeout:
                raise RuntimeError(
                    f"Sgnb telnet phy to cpu {cpu_id} start failed! {self.label} Host: {self.target_host}")
        time.sleep(1)
        telnet_recv(shell_phy)
        print(f"telnet phy to cpu {cpu_id} success! {self.label} Host:{self.target_host}")
        return shell_phy

    def execuate_phy_cmd(self, shell_phy: str, cmd: str, cpu_id: str = '0x20', delay: int = 1) -> str:
        if shell_phy is None:
            print(f"phy to cpu {cpu_id} not connected, trying to connect...{self.label} Host:{self.target_host}")
            shell_phy = self.telnet_PHY(cpu_id)
        shell_phy.send(f'{cmd}\n')
        time.sleep(delay)
        result = telnet_recv(shell_phy)
        if "Idle timeout" in result:
            print(f"phy to cpu {cpu_id} idle, trying to connect...{self.label} Host:{self.target_host}")
            shell_phy = self.telnet_PHY(cpu_id)
            shell_phy.send(f"{cmd}\n")
            time.sleep(delay)
            result = telnet_recv(shell_phy)
        return result
