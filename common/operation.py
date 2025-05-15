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


def execuate_dl_udp_traffic(ue_obj: UeMacServ, amf_obj: AmfServ, filename: str = "dl_udp.txt", bw_size: str = '50m',
                            duration_time: int = 9999, port: int = 5001):
    if ue_obj.ue_ip == '':
        ue_obj.obtain_ue_ip()
        if ue_obj.ue_ip == '':
            raise ValueError(
                f"UE ip is not obtained, execution failed, please try to attach the cell again ! Host:{ue_obj.target_host}")
    ue_obj.execuate_udp_server(filename, port)
    amf_obj.execuate_udp_client(ue_obj.ue_ip, bw_size, duration_time, port)
    # ue_obj.show_udp_rate()


def execuate_ul_udp_traffic(ue_obj: UeMacServ, amf_obj: AmfServ, filename: str = "ul_udp.txt", bw_size: str = '50m',
                            duration_time: int = 9999, port: int = 5001):
    if ue_obj.ue_ip == '':
        ue_obj.obtain_ue_ip()
        if ue_obj.ue_ip == '':
            raise ValueError(
                f"UE ip is not obtained, execution failed, please try to attach the cell again ! Host:{ue_obj.target_host}")
    amf_obj.execuate_udp_server(filename, port)
    ue_obj.execuate_udp_client(amf_obj.target_host, bw_size, duration_time, port)
    # amf_obj.show_udp_rate_plt()
    # amf_obj.show_udp_rate()


def attach_ue(ue_obj_mac: UeMacServ, ue_obj_phy: UePhyServ, timeout: int = 60):
    ue_obj_phy.attach_ue()
    time.sleep(3)
    ue_obj_mac.attach_ue(timeout)
    # ue_obj_mac.check_ue_whether_attach()


def release_ue(ue_obj_mac: UeMacServ, ue_obj_phy: UePhyServ):
    ue_obj_mac.release_ue()
    ue_obj_phy.release_ue()
    time.sleep(3)


def stop_udp_traffic(ue_obj: UeMacServ, amf_obj: AmfServ):
    amf_obj.kill_iperf()
    ue_obj.kill_iperf()


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


def download_log(servs, home_file_path: str, max_workers=3):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(serv.download_log, home_file_path): serv for serv in servs}
        try:
            for future in as_completed(future_to_file):
                future.result()
        except (IOError, FileNotFoundError):
            pass


def update_server_time(servers: list):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cmd = f'date -s "{current_time}"'
    thread_results = {Thread(target=server.exec_server_cmd, args=(cmd, False)): server for server in servers}
    for thread_result in thread_results:
        thread_result.start()
    for thread_result in thread_results:
        thread_result.join()


def exec_ta_cmd(sgnb_serv: SgnbServ):
    ta_cmds = ['xdmaTools 0 0 2100004 1eb',
               'xdmaTools 0 0 2100000 186a',
               'xdmaTools 0 0 2100404 1e',
               'xdmaTools 0 0 2100400 169d',
               'xdmaTools 0 0 2100424 2',
               'xdmaTools 0 0 2c00104 1']
    for cmd in ta_cmds:
        print(sgnb_serv.exec_server_cmd(cmd).strip())


def sgnb_telnet_server(sgnb_serv: SgnbServ):
    tel_l3 = Thread(target=sgnb_serv.telnet_L3)
    tel_l2 = Thread(target=sgnb_serv.telnet_L2)
    tel_phy = Thread(target=sgnb_serv.telnet_PHY)
    tel_l3.start()
    tel_l2.start()
    tel_phy.start()
    tel_l3.join()
    tel_l2.join()
    tel_phy.join()


def fully_automated_upgrade_sgnb_version(
    sgnb_serv: SgnbServ,
    remote_upgrade_path: str = "",
    version_date: str = "",
    sgnb_local_version_path: str = "",
    modify_net_cfg_data= "modify_net_cfg_Data.json",
):
    """
    Perform a fully automated upgrade of the SGNB version.
    This function handles the entire process of upgrading the SGNB version, including downloading the version files,
    uncompressed them, modifying configuration files, compressing the updated files, and uploading them to the remote server.
    Args:
        :param sgnb_serv: An instance of the SgnbServ class, representing the SGNB server.
        :param remote_upgrade_path: The remote path where the upgraded files will be uploaded. Defaults to ''.
        :param version_date: The date of the version to be upgraded. If not provided, the newest version will be used. Defaults to ''.
        :param sgnb_local_version_path: The local path to the version files. If not provided, the files will be downloaded. Defaults to ''.
        :param modify_net_cfg_data:
    Returns:
        None
    """

    if sgnb_local_version_path == "":
        if version_date == "":
            ftp = FtpServ(rbc.get_ftp_cfg())
            sgnb_local_version_path = ftp.download_version_files(ftp.obtain_venus_newest_version()
            )[0]
        else:
            ftp = FtpServ(rbc.get_ftp_cfg())
            sgnb_local_version_path = ftp.download_version_files(ftp.obtain_venus_file(version_date)
            )[0]
    print(sgnb_local_version_path)
    sgnb_uncompress_path = upg.uncompress_tar_gz_file(sgnb_local_version_path)
    nr_cfg_data_path = upg.find_config_file(sgnb_uncompress_path, "nr_cfg_Data.xml")
    data_path = upg.find_config_file(sgnb_uncompress_path, "data.xml")
    scf_gnb_cfg_path = upg.find_config_file(sgnb_uncompress_path, "scf_gNbCfg.json")
    print("modify config file nr_cfg_Data.xml, data.xml and scf_gNbCfg.json")
    upg.modify_xml_file(nr_cfg_data_path, upg.obtain_cfg_json(modify_net_cfg_data))
    upg.modify_xml_file(data_path, upg.obtain_cfg_json(modify_net_cfg_data))
    upg.modify_json_file(scf_gnb_cfg_path, upg.obtain_cfg_json("modify_scf_gNbCfg.json"))
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


def fully_automated_upgrade_ue_version(
    ue_mac_serv: UeMacServ,
    ue_phy_serv: UePhyServ,
    json_template="modify_nrue_cfg_Data.json",
    remote_upgrade_path: str = "",
    version_date: str = "",
    ue_local_version_path: str = "",
):
    """
    Perform a fully automated upgrade of the UE (User Equipment) version.
    This function handles the entire process of upgrading the UE version, including downloading the version files,
    uncompressed them, modifying configuration files, compressing the necessary documents, and uploading them to
    the specified remote paths.
    Args:
        :param ue_mac_serv: The service object for handling UE MAC operations.
        :param ue_phy_serv: The service object for handling UE PHY operations.
        :param json_template:
        :param remote_upgrade_path: The remote path where the upgraded files will be uploaded. Defaults to ''.
        :param version_date: The date of the version to be downloaded. If not provided, the newest version will be used. Defaults to ''.
        :param ue_local_version_path: The local path where the version files are stored. If not provided, the files will be downloaded. Defaults to ''.
    Returns:
        None
    """

    if ue_local_version_path == "":
        if version_date == "":
            ftp = FtpServ(rbc.get_ftp_cfg())
            ue_local_version_path = ftp.download_version_files(
                rbc.LOCAL_LOG_PATH, ftp.obtain_prototype_newest_version()
            )[0]
        else:
            ftp = FtpServ(rbc.get_ftp_cfg())
            ue_local_version_path = ftp.download_version_files(
                rbc.LOCAL_LOG_PATH, ftp.obtain_prototype_file(version_date)
            )[0]
    ue_uncompress_path = upg.uncompress_tar_gz_file(ue_local_version_path)
    ue_mac_cfg_path = upg.find_config_file(ue_uncompress_path, "nrue_cfg_Data.xml")
    print("modify config file nrue_cfg_Data.xml")
    upg.modify_xml_file(ue_mac_cfg_path, upg.obtain_cfg_json(json_template))
    ue_compress_mac_path = upg.organize_compress_ue_documents(
        ue_uncompress_path, "stack"
    )
    ue_compress_phy_path = upg.organize_compress_ue_documents(ue_uncompress_path, "phy")
    if remote_upgrade_path == "":
        remote_upgrade_path = "/".join(ue_mac_serv.exec_path.split("/")[:-1])
    ue_mac_serv.upload_file(ue_compress_mac_path, remote_upgrade_path)
    remote_upgrade_path = ue_phy_serv.exec_path
    ue_phy_serv.upload_file(ue_compress_phy_path, remote_upgrade_path)
    shutil.rmtree(ue_uncompress_path)
    for i in range(rbc.get_ue_len()):
        if rbc.get_ue_mac_cfg(i)["ue_ip"] == ue_mac_serv.target_host:
            rbc.get_ue_mac_cfg(i)["exec_path"] = ue_mac_serv.exec_path
            rbc.modify_basic_cfg()
            break


def local_capture_pcap(path, label: str = ""):
    current_datetime = datetime.now()
    date_format = "%Y-%m-%d_%H_%M_%S"
    formatted_date = current_datetime.strftime(date_format)
    if label != "":
        pcap_filename = f"{path}\\{formatted_date}_{label}.pcap"
    else:
        pcap_filename = f"{path}\\{formatted_date}.pcap"
    proc = subprocess.Popen(
        ["dumpcap", "-i", "6", "-f", "port 54122", "-w", pcap_filename],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    return proc.pid


def stop_local_pcap(pid):
    subprocess.run(["taskkill", "/F", "/PID", str(pid)])

