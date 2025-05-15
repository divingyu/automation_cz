import time
import common.vam as vam
from common.remotePc import PcServ
from common.operation import *

ue_mac_serv = None
ue_phy_serv = None
pc_serv = None

if __name__ == '__main__':
    serv_resource = []
    sgnb_serv_list = []

    try:
        sgnb_a = SgnbServ(rbc.get_sgnb_cfg(), rbc.get_sgnb_name(0))
        sgnb_a.connet_target_sever()
        serv_resource.append(sgnb_a)
        sgnb_serv_list.append(sgnb_a)
        sgnb_b = SgnbServ(rbc.get_sgnb_cfg(1),rbc.get_sgnb_name(1))
        sgnb_b.connet_target_sever()
        serv_resource.append(sgnb_b)
        sgnb_serv_list.append(sgnb_b)
        # 连接终端
        ue_mac_serv = UeMacServ(rbc.get_ue_mac_cfg(),f"{rbc.get_ue_name(0)}_mac")
        ue_mac_serv.connet_target_sever()
        serv_resource.append(ue_mac_serv)

        ue_phy_serv = UePhyServ(rbc.get_ue_phy_cfg(),f"{rbc.get_ue_name(0)}_phy")
        ue_phy_serv.connet_target_sever()
        serv_resource.append(ue_phy_serv)

        update_server_time(serv_resource)
        clean_trace(serv_resource)
        # fully_automated_upgrade_sgnb_version(sgnb_a)
        # fully_automated_upgrade_sgnb_version(sgnb_b)
        for sgnb in sgnb_serv_list:
            sgnb.stop_sgnb_process()

        pc_serv = PcServ(rbc.get_jump_cfg(), label='005_pc')
        pc_serv.connet_target_sever()
        pc_serv.capture_pcap(label='attach', pcap_choice=1, interface=8)

        for sgnb in sgnb_serv_list:
            sgnb.start_sgnb_process(new_architecture=True, is_copy_cfg=True)
        sgnb_a.start_sgnb_scf()
        print(sgnb_a.execuate_scf_cmd('0'))
        print(sgnb_a.execuate_scf_cmd('0'))
        print(sgnb_a.execuate_scf_cmd('4'))
        sgnb_a.telnet_L3()
        print(sgnb_a.execuate_l3_cmd('showCellStatus'))
        print(sgnb_a.execuate_l3_cmd('show_beam_pattern'))
        print(sgnb_a.execuate_l3_cmd('showPhyCellStatus'))
        time.sleep(5)
        vam.block_all_channels(rbc.get_vam_cfg()["vam_ip"],rbc.get_vam_cfg()["vam_port"])
        vam.set_attenuation(rbc.get_vam_cfg()["vam_ip"],rbc.get_vam_cfg()["vam_port"],3,5)
        # 终端发起接入
        attach_ue(ue_mac_serv,ue_phy_serv)
        print(sgnb_a.execuate_l3_cmd("show_all_ue_msg"))

    except KeyboardInterrupt:
        print("KeyboardInterrupt: Exiting the program.")
    finally:
        for sgnb in sgnb_serv_list:
            sgnb.stop_sgnb_process()
        if ue_mac_serv is not None and ue_phy_serv is not None:
            release_ue(ue_mac_serv,ue_phy_serv)
        home_file_path = local_log_path(rbc.LOCAL_LOG_PATH)
        download_log(serv_resource,home_file_path)
        ####清理log####
        if pc_serv is not None:
            pc_serv.stop_pcap(home_file_path, pcap_choice=1)
            pc_serv.closed_ssh()
        clean_trace(serv_resource)
        closed_ssh(serv_resource)