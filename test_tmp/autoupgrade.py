from common.operation import *

serv_resource = []
sgnb_serv_list = []
ue_mac_serv = None
ue_phy_serv = None
pc_serv = None


if __name__ == '__main__':
    # sgnb_a = SgnbServ(rbc.get_sgnb_cfg(), rbc.get_sgnb_name(0))
    # sgnb_a.connet_target_sever()
    # serv_resource.append(sgnb_a)
    # sgnb_serv_list.append(sgnb_a)
    # sgnb_b = SgnbServ(rbc.get_sgnb_cfg(1), rbc.get_sgnb_name(1))
    # sgnb_b.connet_target_sever()
    # serv_resource.append(sgnb_b)
    # sgnb_serv_list.append(sgnb_b)
    # 连接终端
    ue_mac_serv = UeMacServ(rbc.get_ue_mac_cfg(1), f"{rbc.get_ue_name(1)}_mac")
    ue_mac_serv.connet_target_sever()
    serv_resource.append(ue_mac_serv)

    ue_phy_serv = UePhyServ(rbc.get_ue_phy_cfg(1), f"{rbc.get_ue_name(1)}_phy")
    ue_phy_serv.connet_target_sever()
    serv_resource.append(ue_phy_serv)

    update_server_time(serv_resource)
    # fully_automated_upgrade_sgnb_version(sgnb_a)
    # fully_automated_upgrade_sgnb_version(sgnb_b)
    fully_automated_upgrade_ue_version(ue_mac_serv,ue_phy_serv,version_date="20250509120829")
    closed_ssh(serv_resource)