import time
from module.operation_tsx import *
from module import readBasicConfig as rbc
from config.testData import TsxData
from module.singal import Singal

def prach_decode_200M_FM4(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, CNR: str = "-21.54", CP :str = "-41.54", forceinit: bool=False):
    # ###初始化8242
    try:
        D2000V_SGNB_PATH = check_d2000v_exist(sgnbServ,D2000V_PATH) 
        check_fpga_info(sgnbServ)
        if forceinit:
            init_8242(sgnbServ,D2000V_SGNB_PATH)
    except ValueError:
        init_8242(sgnbServ,D2000V_SGNB_PATH)
        check_fpga_info(sgnbServ)
    ###PRACH 测试
    #### 信号源
    instr = Singal(rbc.get_singal_cfg(0)["signal_ip"])
    arb_path = "/var/user/UL_decode_template/PRACH_15KHZ_ARB/BW200M_PRACHformat4_15kHz.wv"
    instr.singal_decode_tmp(arb_path,CNR,CP,clock_freq="245.76MHz",bwid="245.76MHz")

    GTESTPHT = check_gtestphy_exist(sgnbServ,GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    gtestps = start_gtestphy(sgnbServ,GTESTPHT, "5 20000 0 1")
    print(sgnbServ.execuate_phy_cmd("logctrl disable prach info"))
    check_phy_log(sgnbServ)

def prach_decode_200M_FM10(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, CNR: str = "-22.54", CP :str = "-44.54", forceinit: bool=False):
    # ###初始化8242
    try:
        D2000V_SGNB_PATH = check_d2000v_exist(sgnbServ,D2000V_PATH) 
        check_fpga_info(sgnbServ)
        if forceinit:
            init_8242(sgnbServ,D2000V_SGNB_PATH)
    except ValueError:
        init_8242(sgnbServ,D2000V_SGNB_PATH)
        check_fpga_info(sgnbServ)
    ###PRACH 测试
    #### 信号源
    instr = Singal(rbc.get_singal_cfg(0)["signal_ip"])
    arb_path = "/var/user/UL_decode_template/PRACH_15KHZ_ARB/BW200M_PRACHformat10_15kHz.wv"
    instr.singal_decode_tmp(arb_path,CNR,CP,clock_freq="245.76MHz",bwid="245.76MHz")

    GTESTPHT = check_gtestphy_exist(sgnbServ,GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    gtestps = start_gtestphy(sgnbServ,GTESTPHT, "5 20000 0 1")
    print(sgnbServ.execuate_phy_cmd("logctrl disable prach info"))
    check_phy_log(sgnbServ)

def prach_decode_400M_FM4(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, CNR: str = "-24.55", CP :str = "-44.55", forceinit: bool=False):
    # ###初始化8242
    try:
        D2000V_SGNB_PATH = check_d2000v_exist(sgnbServ,D2000V_PATH) 
        check_fpga_info(sgnbServ)
        if forceinit:
            init_8242(sgnbServ,D2000V_SGNB_PATH)
    except ValueError:
        init_8242(sgnbServ,D2000V_SGNB_PATH)
        check_fpga_info(sgnbServ)
    ###PRACH 测试
    #### 信号源
    instr = Singal(rbc.get_singal_cfg(0)["signal_ip"])
    arb_path = "/var/user/UL_decode_template/PRACH_15KHZ_ARB/BW400M_PRACHformat4_15kHz.wv"
    instr.singal_decode_tmp(arb_path,CNR,CP)

    GTESTPHT = check_gtestphy_exist(sgnbServ,GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    gtestps = start_gtestphy(sgnbServ,GTESTPHT, "5 20000 0 1")
    print(sgnbServ.execuate_phy_cmd("logctrl disable prach info"))
    check_phy_log(sgnbServ)

def prach_decode_400M_FM10(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, CNR: str = "-25.55", CP :str = "-45.55", forceinit: bool=False):
    # ###初始化8242
    try:
        D2000V_SGNB_PATH = check_d2000v_exist(sgnbServ,D2000V_PATH)
        check_fpga_info(sgnbServ)
        if forceinit:
            init_8242(sgnbServ,D2000V_SGNB_PATH)
    except ValueError:
        init_8242(sgnbServ,D2000V_SGNB_PATH)
        check_fpga_info(sgnbServ)
    ###PRACH 测试
    #### 信号源
    instr = Singal(rbc.get_singal_cfg(0)["signal_ip"])
    arb_path = "/var/user/UL_decode_template/PRACH_15KHZ_ARB/BW400M_PRACHformat10_15kHz.wv"
    instr.singal_decode_tmp(arb_path,CNR,CP)

    GTESTPHT = check_gtestphy_exist(sgnbServ,GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    gtestps = start_gtestphy(sgnbServ,GTESTPHT, "5 20000 0 1")
    print(sgnbServ.execuate_phy_cmd("logctrl disable prach info"))
    check_phy_log(sgnbServ)

if __name__ == '__main__':
    serv_resouce = []
    try:
        sgnbServ_A = SgnbServ(rbc.get_sgnb_cfg(),rbc.get_sgnb_name(0))
        sgnbServ_A.connet_target_sever()
        serv_resouce.append(sgnbServ_A)
        
        ### 星载1PRACH验证
        #### F1-4为cpu1的波束1的RX0, 200M波束; F1-3为cpu1的波束2的RX1, 400M波束. 当前验证CPU1 的 F1_4
        # prach_decode_200M_FM4(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F1_TX_PRACH_FM4_PATH.value)
        prach_decode_200M_FM10(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F1_TX_PRACH_FM10_PATH.value)
        #### F1-4为cpu1的波束1的RX0, 200M波束; F1-3为cpu1的波束2的RX1, 400M波束. 当前验证CPU1 的 F1_3
        # prach_decode_400M_FM4(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F1_TX_PRACH_FM4_PATH.value)
        # prach_decode_400M_FM10(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F1_TX_PRACH_FM10_PATH.value)
        # #### F2-4为cpu2的波束1的RX0, 200M波束; F2-3为cpu2的波束2的RX1, 200M波束.当前验证CPU2 的 F2_4
        # prach_decode_200M_FM4(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F2_TX_PRACH_FM4_PATH.value)
        # prach_decode_200M_FM10(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F2_TX_PRACH_FM10_PATH.value)
        # #### F2-4为cpu2的波束1的RX0, 200M波束; F2-3为cpu2的波束2的RX1, 200M波束.当前验证CPU2 的 F2_3
        # prach_decode_200M_FM4(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F2_TX_PRACH_FM4_PATH.value)
        # prach_decode_200M_FM10(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F2_TX_PRACH_FM10_PATH.value)


    except KeyboardInterrupt:
        print('Running was interrupted')
    finally:
        instr = Singal(rbc.get_singal_cfg(0)["signal_ip"])
        instr.close_rf()
        kill_gtestphy_ps(sgnbServ_A)
        clean_trace(serv_resouce)
        closed_ssh(serv_resouce)