import time
from module.operation_tsx import *
from module import readBasicConfig as rbc
from module.singal import Singal
from config.testData import TsxData

def pusch_decode_F1_200M_MCS0(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, CNR: str = "-10.05", CP :str = "-9.46",forceinit: bool=False):
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
    arb_path = "/var/user/UL_decode_template/PUSCH_TestCase_200M/MCS0/txWaveformAll_MCS0_200M_128RB.wv"
    instr.singal_decode_tmp(arb_path,CNR,CP)
    # resource_string_1 = f'TCPIP::{rbc.get_singal_cfg(0)["signal_ip"]}::hislip0::INSTR'
    # instr = RsInstrument(resource_string_1, True, False)
    # instr.write_str(f':SOUR1:FREQ {TsxData.SINGAL_MID_FREQ.value}')
    # arb_waveform = "txWaveformAll_MCS0_200M_128RB.wv"
    # instr.write_str(f':SOUR1:BB:ARB:WAV:SEL "/var/user/UL_decode_template/PUSCH_TestCase_200M/MCS0/{arb_waveform}"')
    # instr.write_str(':SOUR1:BB:ARB:CLOCK 491.52MHz')
    # instr.write_str(':SOURce1:BB:ARBitrary:TRIGger:SEQuence SING') 
    # instr.write_str(':SOURce1:BB:ARBitrary:TRIGger:SOURce EGT1') ## 设置为外部触发1
    # instr.write_str(':SOURce1:BB:ARBitrary:TRIGger:EXTernal1:DELay 200') ## 设置外部时延为200 samples
    # instr.write_str(':SOUR1:BB:ARB:STAT ON')
    # instr.write_str(':SOUR1:AWGN:BWID 491.52MHz')
    # instr.write_str(':SOURce1:AWGN:BRATe 336128000')
    # instr.write_str(f':SOUR1:AWGN:SNR {CNR}dB')
    # print(f'"/var/user/UL_decode_template/PUSCH_TestCase_200M/MCS0/{arb_waveform}"')
    # instr.write_str(f':SOUR1:POW {CP}dBm')  # 设置功率为 -30 dBm
    # instr.write_str(':SOUR1:AWGN:STAT ON')  # 启用AWGN
    # # ========== 输出设置 ==========
    # instr.write_str(':OUTP1:STAT ON')  # 开启RF输出
    # instr.close()
    
    GTESTPHT = check_gtestphy_exist(sgnbServ,GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    gtestps = start_gtestphy(sgnbServ,GTESTPHT, "5 20000 0 1")
    dl_xdmas = [
        "xdmaTools 0 0 2500104 fc",
        "xdmaTools 0 0 2500108 3000",
        "xdmaTools 0 0 2600104 fb",
        "xdmaTools 0 0 2600108 4000"
    ]
    for dl_xdma in dl_xdmas:
        print(sgnbServ.exec_server_cmd(dl_xdma,is_print=False))
    print(sgnbServ.execuate_phy_cmd("logctrl disable prach info"))
    check_phy_log(sgnbServ)

def pusch_decode_F1_200M_MCS25(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, CNR: str = "9.95", CP :str = "0.58",forceinit: bool=False):
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
    arb_path = "/var/user/UL_decode_template/PUSCH_TestCase_200M/MCS25/txWaveformAll.wv"
    instr.singal_decode_tmp(arb_path,CNR,CP)
    
    GTESTPHT = check_gtestphy_exist(sgnbServ,GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    gtestps = start_gtestphy(sgnbServ,GTESTPHT, "5 20000 0 1")
    dl_xdmas = [
        "xdmaTools 0 0 2500104 fc",
        "xdmaTools 0 0 2500108 3000",
        "xdmaTools 0 0 2600104 fb",
        "xdmaTools 0 0 2600108 4000"
    ]
    for dl_xdma in dl_xdmas:
        print(sgnbServ.exec_server_cmd(dl_xdma,is_print=False))
    print(sgnbServ.execuate_phy_cmd("logctrl disable prach info"))
    check_phy_log(sgnbServ)

def pusch_decode_F1_400M_MCS0(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, CNR: str = "-7.05", CP :str = "-6.83",forceinit: bool=False):
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
    arb_path = "/var/user/UL_decode_template/PUSCH_TestCase_400M/MCS0/txWaveformAll_mcs0_80slot_400M(1).wv"
    instr.singal_decode_tmp(arb_path,CNR,CP)
    
    GTESTPHT = check_gtestphy_exist(sgnbServ,GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    gtestps = start_gtestphy(sgnbServ,GTESTPHT, "5 20000 0 1")
    dl_xdmas = [
        "xdmaTools 0 0 2500104 fc",
        "xdmaTools 0 0 2500108 3000",
        "xdmaTools 0 0 2600104 fb",
        "xdmaTools 0 0 2600108 4000"
    ]
    for dl_xdma in dl_xdmas:
        print(sgnbServ.exec_server_cmd(dl_xdma,is_print=False))
    print(sgnbServ.execuate_phy_cmd("logctrl disable prach info"))
    check_phy_log(sgnbServ)

def pusch_decode_F1_400M_MCS25(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, CNR: str = "12.95", CP :str = "0.79",forceinit: bool=False):
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
    arb_path = "/var/user/UL_decode_template/PUSCH_TestCase_400M/MCS25/txWaveformAll.wv"
    instr.singal_decode_tmp(arb_path,CNR,CP)
    
    GTESTPHT = check_gtestphy_exist(sgnbServ,GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    gtestps = start_gtestphy(sgnbServ,GTESTPHT, "5 20000 0 1")
    dl_xdmas = [
        "xdmaTools 0 0 2500104 fc",
        "xdmaTools 0 0 2500108 3000",
        "xdmaTools 0 0 2600104 fb",
        "xdmaTools 0 0 2600108 4000"
    ]
    for dl_xdma in dl_xdmas:
        print(sgnbServ.exec_server_cmd(dl_xdma,is_print=False))
    print(sgnbServ.execuate_phy_cmd("logctrl disable prach info"))
    check_phy_log(sgnbServ)

def pusch_decode_F2_200M_MCS0(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, forceinit: bool=False, CNR: str = "-10.05", CP :str = "-9.46"):
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
    arb_path = "/var/user/UL_decode_template/PUSCH_TestCase_200M/MCS0/txWaveformAll_MCS0_200M_128RB.wv"
    instr.singal_decode_tmp(arb_path,CNR,CP)
    
    GTESTPHT = check_gtestphy_exist(sgnbServ,GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    gtestps = start_gtestphy(sgnbServ,GTESTPHT, "5 20000 0 1")
    dl_xdmas = [
        "xdmaTools 0 0 2500104 fc",
        "xdmaTools 0 0 2500108 3000",
        "xdmaTools 0 0 2600104 fc",
        "xdmaTools 0 0 2500108 4000",
        "xdmaTools 0 0 200002c 2",
        "xdmaTools 0 0 2000030 3"
    ]
    for dl_xdma in dl_xdmas:
        print(sgnbServ.exec_server_cmd(dl_xdma,is_print=False))
    print(sgnbServ.execuate_phy_cmd("logctrl disable prach info"))
    check_phy_log(sgnbServ)

def pusch_decode_F2_200M_MCS25(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, forceinit: bool=False, CNR: str = "9.95", CP :str = "0.58"):
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
    arb_path = "/var/user/UL_decode_template/PUSCH_TestCase_200M/MCS25/txWaveformAll.wv"
    instr.singal_decode_tmp(arb_path,CNR,CP)
    
    GTESTPHT = check_gtestphy_exist(sgnbServ,GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    gtestps = start_gtestphy(sgnbServ,GTESTPHT, "5 20000 0 1")
    dl_xdmas = [
        "xdmaTools 0 0 2500104 fc",
        "xdmaTools 0 0 2500108 3000",
        "xdmaTools 0 0 2600104 fc",
        "xdmaTools 0 0 2500108 4000",
        "xdmaTools 0 0 200002c 2",
        "xdmaTools 0 0 2000030 3"
    ]
    for dl_xdma in dl_xdmas:
        print(sgnbServ.exec_server_cmd(dl_xdma,is_print=False))
    print(sgnbServ.execuate_phy_cmd("logctrl disable prach info"))
    check_phy_log(sgnbServ)

if __name__ == '__main__':
    serv_resouce = []

    try:
        sgnbServ_A = SgnbServ(rbc.get_sgnb_cfg(),rbc.get_sgnb_name(0))
        sgnbServ_A.connet_target_sever()
        serv_resouce.append(sgnbServ_A)
        
        ### 星载1PUSCH验证
        #### F1-4为cpu1的波束1的RX0, 200M波束; F1-3为cpu1的波束2的RX1, 400M波束. 当前验证CPU1 的 F1_4
        # pusch_decode_F1_200M_MCS0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHY_F1_RX0_MCS0_PATH.value)
        # pusch_decode_F1_200M_MCS0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHY_F1_RX0_MCS0_PATH.value,CP="-29.46")
        # pusch_decode_F1_200M_MCS0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHY_F1_RX0_MCS0_PATH.value,CP="-49.96")
        # pusch_decode_F1_200M_MCS25(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHY_F1_RX0_MCS25_PATH.value)
        # pusch_decode_F1_200M_MCS25(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHY_F1_RX0_MCS25_PATH.value,CP="-19.42")
    
        #### F1-4为cpu1的波束1的RX0, 200M波束; F1-3为cpu1的波束2的RX1, 400M波束. 当前验证CPU1 的 F1_3
        # pusch_decode_F1_400M_MCS0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHY_F1_RX1_MCS0_PATH.value)
        # pusch_decode_F1_400M_MCS0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHY_F1_RX1_MCS0_PATH.value, CP="-26.83")
        # pusch_decode_F1_400M_MCS0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHY_F1_RX1_MCS0_PATH.value, CP="-47.33")
        # pusch_decode_F1_400M_MCS25(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHY_F1_RX1_MCS25_PATH.value)
        pusch_decode_F1_400M_MCS25(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHY_F1_RX1_MCS25_PATH.value,CP="-19.21")
        
        
        #### F2-4为cpu2的波束1的RX0, 200M波束; F2-3为cpu2的波束2的RX1, 200M波束. 当前验证CPU2 的 F2_4
        # pusch_decode_F2_200M_MCS0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F2_RX0_MCS0_PATH.value)
        # pusch_decode_F2_200M_MCS0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F2_RX0_MCS0_PATH.value,CP="-29.46")
        # pusch_decode_F2_200M_MCS0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F2_RX0_MCS0_PATH.value,CP="-49.96")
        # pusch_decode_F2_200M_MCS25(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F2_RX0_MCS25_PATH.value)
        # pusch_decode_F2_200M_MCS25(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F2_RX0_MCS25_PATH.value,  CP="-19.42")
        # #### F2-4为cpu2的波束1的RX0, 200M波束; F2-3为cpu2的波束2的RX1, 200M波束. 当前验证CPU2 的 F2_3
        # pusch_decode_F2_200M_MCS0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F2_RX1_MCS0_PATH.value)
        # pusch_decode_F2_200M_MCS0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F2_RX1_MCS0_PATH.value,CP="-29.46")
        # pusch_decode_F2_200M_MCS0(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F2_RX1_MCS0_PATH.value,CP="-49.96")
        # pusch_decode_F2_200M_MCS25(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F2_RX1_MCS25_PATH.value)
        # pusch_decode_F2_200M_MCS25(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value, TsxData.GTESTPHT_F2_RX1_MCS25_PATH.value,CP="-19.42")


    except KeyboardInterrupt:
        print('Running was interrupted')
    finally:
        instr = Singal(rbc.get_singal_cfg(0)["signal_ip"])
        instr.close_rf()
        kill_gtestphy_ps(sgnbServ_A)
        # clean_trace(serv_resouce)
        closed_ssh(serv_resouce)