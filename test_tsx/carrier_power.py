import re
from module.operation_tsx import *
from module import readBasicConfig as rbc
from config.testData import TsxData

def carrier_power_F1(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, forceinit: bool=False):
    # ###初始化8242
    try:
        D2000V_SGNB_PATH = check_d2000v_exist(sgnbServ,D2000V_PATH) 
        check_fpga_info(sgnbServ)
        if forceinit:
            init_8242(sgnbServ,D2000V_SGNB_PATH)
    except ValueError:
        init_8242(sgnbServ,D2000V_SGNB_PATH)
        check_fpga_info(sgnbServ)
    ###F1 子载波测试
    GTESTPHT = check_gtestphy_exist(sgnbServ, GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    print("复位CPU")
    fucmd = "xdmaTools 0 0 0x01000800 1;xdmaTools 0 0 0x01000800 0;xdmaTools 0 0 02a00004 1;xdmaTools 0 0 02a00004"
    print(sgnbServ.exec_server_cmd(fucmd,is_print=False).strip())
    gtestps = start_gtestphy(sgnbServ, GTESTPHT, "5 20000 0 1")
    
    ###F1 时域功控
    time_power_list = [
        "xdmaTools 0 0 2500104 fc",
        "xdmaTools 0 0 2600104 fc",
        "xdmaTools 0 0 2500108 3500"
    ]
    for time_power in time_power_list:
        print(sgnbServ.exec_server_cmd(time_power,is_print=False).strip())
    
    ###检查频谱仪载波功率
    print("CPU1的F1-2为400M, F1-1,F2-1,F2-2都为200M\n"\
            "如果频谱仪连接的F1-1,则 MEAS COFIG -> CP/ACLRStandard -> 5G NR DL FR2 100MHz\n"\
            "第一个载波, 中心频率设置为2200M, 读取功率P1, 第二个载波, 中心频率设置为2300M, 读取功率为P2, 功率差∆P=|P2-P1|, 要求小于6db\n"\
            "如果频谱仪连接的F1-2,则 MEAS COFIG -> CP/ACLRStandard -> 5G NR DL FR2 200MHz\n"\
            "第一个载波, 中心频率设置为2150M, 读取功率P1, 第二个载波, 中心频率设置为2350M, 读取功率为P2, 功率差∆P=|P2-P1|, 要求小于6db")
    while True:
        power1 = input("请输入第一个载波的功率值: ")
        if re.match(r"^-?[0-9]+\.?[0-9]*$",power1):
            break
        else:
            print("第一个载波功率值输入格式不对, 请重新输入!!!")

    while True:
        power2 = input("请输入第二个载波的功率值: ")
        if re.match(r"^-?[0-9]+\.?[0-9]*$",power2):
            break
        else:
            print("第二个载波功率值输入格式不对, 请重新输入!!!")
    print(f"子载波功率为{round(float(power2)-float(power1),2)}")


def carrier_power_F2(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, forceinit: bool=False):
    try:
        D2000V_SGNB_PATH = check_d2000v_exist(sgnbServ,D2000V_PATH) 
        check_fpga_info(sgnbServ)
        if forceinit:
            init_8242(sgnbServ,D2000V_SGNB_PATH)
    except ValueError:
        init_8242(sgnbServ,D2000V_SGNB_PATH)
        check_fpga_info(sgnbServ)
    ###F2 子载波测试
    GTESTPHT = check_gtestphy_exist(sgnbServ, GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    print("复位CPU")
    fucmd = "xdmaTools 0 0 0x01000800 1;xdmaTools 0 0 0x01000800 0;xdmaTools 0 0 02a00004 1;xdmaTools 0 0 02a00004"
    print(sgnbServ.exec_server_cmd(fucmd,is_print=False).strip())
    gtestps = start_gtestphy(sgnbServ, GTESTPHT, "5 20000 0 1")
    ###F1 时域功控
    time_power_list = [
        "xdmaTools 0 0 2500104 fc",
        "xdmaTools 0 0 2500108 3500",
        "xdmaTools 0 0 2600104 fc",
        "xdmaTools 0 0 2600108 2500",
        "xdmaTools 0 0 200002c 2",
        "xdmaTools 0 0 2000030 3"
    ]
    for time_power in time_power_list:
        print(sgnbServ.exec_server_cmd(time_power,is_print=False).strip())
    
    ###检查频谱仪载波功率
    print("CPU1的F1-2为400M, F1-1,F2-1,F2-2都为200M\n"\
            "频谱仪连接的F2-1, F2-2, 频谱仪都配为 MEAS COFIG -> CP/ACLRStandard -> 5G NR DL FR2 100MHz\n"\
            "第一个载波, 中心频率设置为2200M, 读取功率P1, 第二个载波, 中心频率设置为2300M, 读取功率为P2, 功率差∆P=|P2-P1|, 要求小于6db")
    while True:
        power1 = input("请输入第一个载波的功率值: ")
        if re.match(r"^-?[0-9]+\.?[0-9]*$",power1):
            break
        else:
            print("第一个载波功率值输入格式不对, 请重新输入!!!")

    while True:
        power2 = input("请输入第二个载波的功率值: ")
        if re.match(r"^-?[0-9]+\.?[0-9]*$",power2):
            break
        else:
            print("第二个载波功率值输入格式不对, 请重新输入!!!")
    print(f"子载波功率为{round(float(power2)-float(power1),2)}")
    
if __name__ == '__main__':
    serv_resouce = []

    try:
        sgnbServ_A = SgnbServ(rbc.get_sgnb_cfg(),rbc.get_sgnb_name(0))
        sgnbServ_A.connet_target_sever()
        serv_resouce.append(sgnbServ_A)
        
        ### 星载1子载波功率验证
        #### F1-1为cpu1的波束1的TX0, 200M波束; F1-2为cpu1的波束2的TX1, 400M波束, 测F1-1 和 F1-2
        carrier_power_F1(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value,TsxData.GTESTPHT_F1_TX_SUB_PATH.value)
        # #### F2-1为cpu2的波束1的TX0, 200M波束; F2-2为cpu2的波束2的TX1, 200M波束, 测 F2-1 和 F2-2
        # carrier_power_F2(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value,TsxData.GTESTPHT_F2_TX_SUB_PATH.value)

    except KeyboardInterrupt:
        print('Running was interrupted')
    finally:
        kill_gtestphy_ps(sgnbServ_A)
        closed_ssh(serv_resouce)