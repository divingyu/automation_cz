"""
Company            :
Create Date        : 2025-01-24 14:48:11
Engineer           : You Yuling
Target Devices     : operation method
Tool Versions      : v_1.0
Description        :
Revision           : LastEditTime
"""
import os
import re
import time
import shutil
import subprocess
import common.readBasicConfig as rbc
import common.upgrade as upg
from threading import Thread
from datetime import datetime
from common.amf import AmfServ
from common.sgnb import SgnbServ
from common.ueMac import UeMacServ
from common.uePhy import UePhyServ
from common.version import FtpServ
from concurrent.futures import ThreadPoolExecutor, as_completed


def closed_ssh(servers: list):
    for server in servers:
        server.closed_ssh()


def clean_trace(serves: list):
    for server in serves:
        server.clean_log_trace()


def local_log_path(home_path, suffix_name: str = ""):
    if home_path == "":
        raise ValueError("Please input local_log_path in config.json!!!")
    if not os.path.isdir(home_path):
        raise ValueError("Please check path is correct!!!")
    return generate_new_pwd(home_path, suffix_name)


def generate_new_pwd(current_pwd: str, suffix_name: str = "") -> str:
    current_datetime = datetime.now()
    date_format = "%Y-%m-%d_%H_%M_%S"
    formatted_date = current_datetime.strftime(date_format)
    if suffix_name == "":
        new_pwd = f"{current_pwd}\\{formatted_date}"
    else:
        new_pwd = f"{current_pwd}\\{formatted_date}_{suffix_name}"
    if not os.path.exists(new_pwd):
        os.mkdir(new_pwd)
    return new_pwd


def download_log(servs, home_file_path: str, max_workers = 3):
    with ThreadPoolExecutor(max_workers = max_workers) as executor:
        future_to_file = {
            executor.submit(serv.download_log, home_file_path):serv for serv in servs
        }
        try:
            for future in as_completed(future_to_file):
                future.result()
        except (IOError, FileNotFoundError):
            pass


def init_8242(gnb_serv: SgnbServ, d2000v_sgnb_path: str):
    init_cmd = f"cd {d2000v_sgnb_path} && ./start.sh -f 2.25G -C -s 0"
    stdin, stdout, stderr = gnb_serv.target_ssh_client.exec_command(init_cmd)
    channel = stdout.channel
    while not channel.exit_status_ready():
        if channel.recv_ready():
            output = channel.recv(1024).decode('utf-8')
            print(output, end = "")
    # kill 8242 进程
    current_time = datetime.now().timestamp()
    print("checking adda ... (init 8242)")
    while True:
        if check_addr_is_ok(gnb_serv):
            break
        nowtime = datetime.now().timestamp()
        if int(nowtime - current_time) > 60:
            raise ValueError(
                    f"adda check failed! {gnb_serv.label} Host: {gnb_serv.target_host}"
            )
        time.sleep(2)
    kill_init_cmd = f"cd {d2000v_sgnb_path} && ./kill.sh"
    gnb_serv.exec_server_cmd(kill_init_cmd, is_print = False)


def check_addr_is_ok(sgnb_serv: SgnbServ):
    addr_dict = {
        "xdmaTools 0 0 2900000 0x51f":"0000051F",
        "xdmaTools 0 0 2900008 1":"00000001",
        "xdmaTools 0 0 2900008 0":"00000000",
        "xdmaTools 0 0 2b00150":"00000003",
        "xdmaTools 0 0 2b00154":"000000AA"
    }
    for addr_cmd, value in addr_dict.items():
        result = sgnb_serv.exec_server_cmd(addr_cmd, is_print = False)
        if result.strip() != value:
            return False
    return True


def check_fpga_info(sgnb_serv: SgnbServ):
    fpga_sym_cmd = "xdmaTools 0 0 0x2000004"
    result = re.match(r"[\dA-F]+", sgnb_serv.exec_server_cmd(fpga_sym_cmd, is_print = False))
    if result and result.group(0) != "FFFFFFFF":
        print(f"FPGA symbol version is {result.group(0)}")
    else:
        raise ValueError("FPGA symbol version error")
    fpga_bit_cmd = "xdmaTools 0 0 0x1000004"
    result = re.match(r"[\dA-F]+", sgnb_serv.exec_server_cmd(fpga_bit_cmd, is_print = False))
    if result and result.group(0) != "FFFFFFFF":
        print(f"FPGA symbol version is {result.group(0)}")
    else:
        raise ValueError("FPGA symbol version error")
    current_time = datetime.now().timestamp()
    print("checking adda ...(check fpga)")
    while True:
        if check_addr_is_ok(sgnb_serv):
            break
        nowtime = datetime.now().timestamp()
        if int(nowtime - current_time) > 30:
            raise ValueError(
                    f"adda check failed! {sgnb_serv.label} Host: {sgnb_serv.target_host}"
            )
        time.sleep(2)


def kill_gtestphy_ps(sgnb_serv: SgnbServ):
    kill_cmd = "ps -ef | grep 'tail' | grep -v grep | awk '{print $2}' | xargs -I {} kill -9 {}"
    sgnb_serv.exec_server_cmd(kill_cmd, is_print = False)
    kill_cmd = "ps -ef | grep gtestphy | grep -v grep | awk '{print $2}' | xargs -I {} kill -9 {}"
    sgnb_serv.exec_server_cmd(kill_cmd, is_print = False)
    clean_cmd = f"cd {sgnb_serv.log_path}/l1 && rm -rf *"
    sgnb_serv.exec_server_cmd(clean_cmd, is_print = False)


def start_gtestphy(sgnb_serv: SgnbServ, gtestphy_path: str, suffix: str = "5 20000 0 1"):
    gettest_s = f"find {gtestphy_path} -name 'gtestphy*' -type f"
    gettest_cmd = sgnb_serv.exec_server_cmd(gettest_s, is_print = False)
    if gettest_cmd == "":
        raise ValueError("gtestphy not exist")
    gettest_cmd = gettest_cmd.strip().split("/")[-1]
    gtestphy_cmd = f"cd {gtestphy_path} && ./{gettest_cmd} {suffix}"
    print(gtestphy_cmd)
    current_time = datetime.now().timestamp()
    timeout = 30
    gtestps = sgnb_serv.target_ssh_client.invoke_shell()
    while not gtestps.recv_ready():
        time.sleep(1)
    gtestps.send(f"{gtestphy_cmd}\n")
    while True:
        output = gtestps.recv(1024).decode()
        print(output)
        if "log file" in output:
            break
        time.sleep(1)
        nowtime = datetime.now().timestamp()
        if nowtime - current_time > timeout:
            raise RuntimeError(
                    f"gTestPhy start failed! {sgnb_serv.label} Host: {sgnb_serv.target_host}"
            )
    return gtestps


def check_phy_log(sgnb_serv: SgnbServ):
    # cmd = f"tail -f {sgnbServ.log_path}/l1/phy_*| grep -E 'UL PROC THPT = [1-9]\\d*'"
    cmd = f"tail -f {sgnb_serv.log_path}/l1/phy_*"
    stdin, stdout, stderr = sgnb_serv.target_ssh_client.exec_command(cmd)
    channel = stdout.channel
    time.sleep(0.1)
    while not channel.exit_status_ready() or channel.recv_ready():
        if channel.recv_ready():
            output = channel.recv(1024).decode('utf-8')
            print(output, end = "")
    exitstatus = channel.recv_exit_status()
    print(f"\ncommand exit status is {exitstatus}")


def update_server_time(servers: list):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cmd = f'date -s "{current_time}"'
    thread_results = {
        Thread(target = server.exec_server_cmd, args = (cmd, False)):server
        for server in servers
    }
    for thread_result in thread_results:
        thread_result.start()
    for thread_result in thread_results:
        thread_result.join()


def exec_ta_cmd(sgnb_serv: SgnbServ):
    ta_cmds = [
        "xdmaTools 0 0 2100024 4e",
        "xdmaTools 0 0 2100424 4e",
        "xdmaTools 0 0 2100400 16c1",
        "xdmaTools 0 0 2100404 42",
        "xdmaTools 0 0 2100000 16c1",
        "xdmaTools 0 0 2100004 42",
    ]
    # ta_cmds = [ 'xdmaTools 0 0 2100004 1eb',
    #             'xdmaTools 0 0 2100000 186a',
    #             'xdmaTools 0 0 2100404 1e',
    #             'xdmaTools 0 0 2100400 169d',
    #             'xdmaTools 0 0 2100424 2',
    #             'xdmaTools 0 0 2c00104 1']
    for cmd in ta_cmds:
        print(sgnb_serv.exec_server_cmd(cmd).strip())


def sgnb_telnet_server(sgnb_serv: SgnbServ):
    tel_l3 = Thread(target = sgnb_serv.telnet_L3)
    tel_l2 = Thread(target = sgnb_serv.telnet_L2)
    tel_phy = Thread(target = sgnb_serv.telnet_PHY)
    tel_l3.start()
    tel_l2.start()
    tel_phy.start()
    tel_l3.join()
    tel_l2.join()
    tel_phy.join()


def check_d2000v_exist(sgnb_serv: SgnbServ, d2000v_path):
    d2000v_name = os.path.basename(d2000v_path)
    remote_fixed_path = "/root/D2000V"
    remote_d2000v_path = f"/root/{d2000v_name}"
    sftp_client = sgnb_serv.target_ssh_client.get_transport().open_sftp_client()
    try:
        sftp_client.stat(remote_fixed_path)
        if not sftp_client.listdir(remote_fixed_path):
            raise IOError(f"{remote_fixed_path} is empty folder")
        else:
            print(f"D2000V already exists in {sgnb_serv.target_host}")
            return remote_fixed_path
    except IOError:
        print(f"{remote_fixed_path} doesn't exist in {sgnb_serv.target_host}")
        if os.path.exists(f"{d2000v_path}.tar.gz"):
            print(f"{d2000v_name}.tar.gz already exists")
            compress_path = f"{d2000v_path}.tar.gz"
        else:
            compress_path = upg.compress_folder(d2000v_path)
        print(f"upload {d2000v_name}.tar.gz to {sgnb_serv.target_host}")
        sgnb_serv.upload_cfg_file(compress_path, f"{remote_d2000v_path}.tar.gz")
        sgnb_serv.exec_server_cmd(f"tar -zxvf {remote_d2000v_path}.tar.gz -C /root/", is_print = False)
        sgnb_serv.exec_server_cmd(f"rm -rf {remote_d2000v_path}.tar.gz", is_print = False)
        sgnb_serv.exec_server_cmd(f"chmod +x -R {remote_d2000v_path}/*", is_print = False)
        sgnb_serv.exec_server_cmd(f"mv {remote_d2000v_path} {remote_fixed_path}", is_print = False)
        return remote_fixed_path


def check_gtestphy_exist(sgnb_serv: SgnbServ, gtestphy_path):
    gtestphy_name = os.path.basename(gtestphy_path)
    remote_gtestphy_path = f"/root/{gtestphy_name}"
    sftp_client = sgnb_serv.target_ssh_client.get_transport().open_sftp_client()
    try:
        sftp_client.stat(remote_gtestphy_path)
        if not sftp_client.listdir(remote_gtestphy_path):
            raise IOError(f"{remote_gtestphy_path} is empty folder")
        else:
            print(f"{remote_gtestphy_path} already exists in {sgnb_serv.target_host}")
            return remote_gtestphy_path
    except IOError:
        print(f"{remote_gtestphy_path} doesn't exist in {sgnb_serv.target_host}")
        if os.path.exists(f"{gtestphy_path}.tar.gz"):
            print(f"{gtestphy_name}.tar.gz already exists")
            compress_path = f"{gtestphy_path}.tar.gz"
        else:
            compress_path = upg.compress_folder(gtestphy_path)
        print(f"upload {gtestphy_name}.tar.gz to {sgnb_serv.target_host}")
        sgnb_serv.upload_cfg_file(compress_path, f"{remote_gtestphy_path}.tar.gz")
        sgnb_serv.exec_server_cmd(f"tar -zxvf {remote_gtestphy_path}.tar.gz -C /root/", is_print = False)
        sgnb_serv.exec_server_cmd(f"rm -rf {remote_gtestphy_path}.tar.gz", is_print = False)
        sgnb_serv.exec_server_cmd(f"chmod +x -R {remote_gtestphy_path}/*", is_print = False)
        return remote_gtestphy_path


# def check_gtestphy_exist(sgnbServ: SgnbServ, gtestphy_path):
#     gtestphy_name = os.path.basename(gtestphy_path)
#     remote_gtestphy_path = f"/root/{gtestphy_name}"
#     stdin, stdout, stderr  = sgnbServ.target_ssh_client.exec_command(f"ls {remote_gtestphy_path}")
#     if stderr.read().decode() != "":
#         print(f"{gtestphy_name} doesn't exist in {sgnbServ.target_host}")
#         if os.path.exists(f"{gtestphy_path}.tar.gz"):
#             print(f"{gtestphy_name}.tar.gz already exists")
#             compress_path = f"{gtestphy_path}.tar.gz"
#         else:
#             compress_path = upg.compress_folder(gtestphy_path)
#         print(f"upload {gtestphy_name}.tar.gz to {sgnbServ.target_host}")
#         sgnbServ.upload_cfg_file(compress_path, f"{remote_gtestphy_path}.tar.gz")
#         sgnbServ.exec_server_cmd(f"tar -zxvf {remote_gtestphy_path}.tar.gz -C /root/",is_print=False)
#         sgnbServ.exec_server_cmd(f"rm -rf {remote_gtestphy_path}.tar.gz",is_print=False)
#         sgnbServ.exec_server_cmd(f"chmod +x -R {remote_gtestphy_path}/*",is_print=False)
#     else:
#         print(f"{gtestphy_name} already exists in {sgnbServ.target_host}")
#     return remote_gtestphy_path

def fully_automated_upgrade_sgnb_version(
        sgnb_serv: SgnbServ,
        remote_upgrade_path: str = "",
        version_date: str = "",
        sgnb_local_version_path: str = "",
        modify_net_cfg_data = "modify_net_cfg_Data.json",
):
    """
    Perform a fully automated upgrade of the SGNB version.
    This function handles the entire process of upgrading the SGNB version, including downloading the version files,
    uncompressed them, modifying configuration files, compressing the updated files, and uploading them to the
    remote server.
    Args:
        sgnb_serv (SgnbServ): An instance of the SgnbServ class, representing the SGNB server.
        remote_upgrade_path (str, optional): The remote path where the upgraded files will be uploaded. Defaults to ''.
        version_date (str, optional): The date of the version to be upgraded. If not provided, the newest version
        will be used. Defaults to ''.
        sgnb_local_version_path (str, optional): The local path to the version files. If not provided, the files will
        be downloaded. Defaults to ''.
    Returns:
        None
    """

    if sgnb_local_version_path == "":
        if version_date == "":
            ftp = FtpServ(rbc.get_ftp_cfg())
            sgnb_local_version_path = ftp.download_version_files(
                    rbc.LOCAL_LOG_PATH, ftp.obtain_venus_newest_version()
            )[0]
        else:
            ftp = FtpServ(rbc.get_ftp_cfg())
            sgnb_local_version_path = ftp.download_version_files(
                    rbc.LOCAL_LOG_PATH, ftp.obtain_venus_file(version_date)
            )[0]
    print(sgnb_local_version_path)
    sgnb_uncompress_path = upg.uncompress_tar_gz_file(sgnb_local_version_path)
    nr_cfg_data_path = upg.find_config_file(sgnb_uncompress_path, "nr_cfg_Data.xml")
    data_path = upg.find_config_file(sgnb_uncompress_path, "data.xml")
    scf_gnbcfg_path = upg.find_config_file(sgnb_uncompress_path, "scf_gNbCfg.json")
    print("modify config file nr_cfg_Data.xml, data.xml and scf_gNbCfg.json")
    upg.modify_xml_file(nr_cfg_data_path, upg.obtain_cfg_json(modify_net_cfg_data))
    upg.modify_xml_file(data_path, upg.obtain_cfg_json(modify_net_cfg_data))
    upg.modify_json_file(scf_gnbcfg_path, upg.obtain_cfg_json("modify_scf_gNbCfg.json"))
    sgnb_compress_path = upg.organize_compress_sgnb_documents(sgnb_uncompress_path)
    if remote_upgrade_path == "":
        remote_upgrade_path = "/".join(sgnb_serv.exec_path.split("/")[:-1])
    sgnb_serv.upload_file(sgnb_compress_path, remote_upgrade_path)
    sgnb_serv.update_bsp(upg.find_config_file(sgnb_uncompress_path, "rootfs_venus.img"))
    shutil.rmtree(sgnb_uncompress_path)
    for i in range(rbc.get_sgnb_len()):
        if rbc.get_sgnb_cfg(i)["sgnb_ip"] == sgnb_serv.target_host:
            rbc.get_sgnb_cfg(i)["exec_path"] = sgnb_serv.exec_path
            rbc.modify_basic_cfg()
            break


if __name__ == "__main__":
    # sgnb = SgnbServ(rbc.get_sgnb_cfg())
    # sgnb.connet_target_sever()
    # local_version_path = r'C:\Users\Lenovo\Desktop\automation\version\S-gNB6810_V921R001C010SPC100B040
    # .20250124164310.tar.gz
    # fully_automated_upgrade_sgnb_version(sgnb,sgnb_local_version_path=local_version_path)
    pass
