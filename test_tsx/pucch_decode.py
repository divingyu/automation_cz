import time
from module.operation_tsx import *
from module import readBasicConfig as rbc
from config.testData import TsxData
from module.singal import Singal

def pucch_decode_200M_FM0(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, CNR: str = "-24.62", CP :str = "-44.62",forceinit: bool=False):
    # ###初始化8242
    try:
        D2000V_SGNB_PATH = check_d2000v_exist(sgnbServ,D2000V_PATH) 
        check_fpga_info(sgnbServ)
        if forceinit:
            init_8242(sgnbServ,D2000V_SGNB_PATH)
    except ValueError:
        init_8242(sgnbServ,D2000V_SGNB_PATH)
        check_fpga_info(sgnbServ)
    ###PUSCH 测试
    #### 信号源
    instr = Singal(rbc.get_singal_cfg(0)["signal_ip"])
    arb_path = "/var/user/UL_decode_template/PUCCH_ARB/case3_PUCCH0_200M.wv"
    instr.singal_decode_tmp(arb_path,CNR,CP)
    
    GTESTPHT = check_gtestphy_exist(sgnbServ,GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    gtestps = start_gtestphy(sgnbServ,GTESTPHT, "5 20000 0 1")
    print(sgnbServ.execuate_phy_cmd("logctrl disable prach info"))
    print(sgnbServ.execuate_phy_cmd("paramSet pucch pucchPayload 2"))
    check_phy_log(sgnbServ)

def pucch_decode_400M_FM0(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, CNR: str = "-24.82", CP :str = "-44.82",forceinit: bool=False):
    # ###初始化8242
    try:
        D2000V_SGNB_PATH = check_d2000v_exist(sgnbServ,D2000V_PATH) 
        check_fpga_info(sgnbServ)
        if forceinit:
            init_8242(sgnbServ,D2000V_SGNB_PATH)
    except ValueError:
        init_8242(sgnbServ,D2000V_SGNB_PATH)
        check_fpga_info(sgnbServ)
    ###PUSCH 测试
    #### 信号源
    instr = Singal(rbc.get_singal_cfg(0)["signal_ip"])
    arb_path = "/var/user/UL_decode_template/PUCCH_ARB/case1_PUCCH0_400M.wv"
    instr.singal_decode_tmp(arb_path,CNR,CP)
    
    GTESTPHT = check_gtestphy_exist(sgnbServ,GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    gtestps = start_gtestphy(sgnbServ,GTESTPHT, "5 20000 0 1")
    print(sgnbServ.execuate_phy_cmd("logctrl disable prach info"))
    print(sgnbServ.execuate_phy_cmd("paramSet pucch pucchPayload 2"))
    check_phy_log(sgnbServ)

if __name__ == '__main__':
    serv_resouce = []

    try:
        sgnbServ_A = SgnbServ(rbc.get_sgnb_cfg(),rbc.get_sgnb_name(0))
        sgnbServ_A.connet_target_sever()
        serv_resouce.append(sgnbServ_A)
        
        ### 星载1PUCCH验证
        #### F1-4为cpu1的波束1的RX0, 200M波束; F1-3为cpu1的波束2的RX1, 400M波束. 当前验证CPU1 的 F1_4
        pucch_decode_200M_FM0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHY_RX0_PUCCH_F1_FM0.value)
        # #### F1-4为cpu1的波束1的RX0, 200M波束; F1-3为cpu1的波束2的RX1, 400M波束. 当前验证CPU1 的 F1_3
        # pucch_decode_400M_FM0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHY_RX1_PUCCH_F1_FM0.value)
        # #### F2-4为cpu2的波束1的TX0, 200M波束; F2-3为cpu2的波束2的TX1, 200M波束. 当前验证CPU2 的 F2_4
        # pucch_decode_200M_FM0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHY_RX0_PUCCH_F2_FM0.value)
        # #### F2-4为cpu2的波束1的TX0, 200M波束; F2-3为cpu2的波束2的TX1, 200M波束. 当前验证CPU2 的 F2_3
        # pucch_decode_200M_FM0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHY_RX1_PUCCH_F2_FM0.value)

    except KeyboardInterrupt:
        print('Running was interrupted')
    finally:
        instr = Singal(rbc.get_singal_cfg(0)["signal_ip"])
        instr.close_rf()
        kill_gtestphy_ps(sgnbServ_A)
        clean_trace(serv_resouce)
        closed_ssh(serv_resouce)