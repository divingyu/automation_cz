from module.operation_tsx import *
from module import readBasicConfig as rbc
from config.testData import TsxData
import re
import math
import random

def rx_tx_lsolation(sgnbServ: SgnbServ, D2000V_PATH:str, forceinit: bool=False):
    ###初始化8242
    try:
        D2000V_SGNB_PATH = check_d2000v_exist(sgnbServ,D2000V_PATH) 
        check_fpga_info(sgnbServ)
        if forceinit:
            init_8242(sgnbServ,D2000V_SGNB_PATH)
    except ValueError:
        init_8242(sgnbServ,D2000V_SGNB_PATH)
        check_fpga_info(sgnbServ)
    
    ###收发隔离度, tx1 发单音
    time_power_list = [
        "xdmaTools 0 0 2b0016c 2",
        "xdmaTools 0 0 2b00240 0",
        "xdmaTools 0 0 2b00244 5355555",
        "xdmaTools 0 0 2b00248 0x6fff"
    ]
    for time_power in time_power_list:
        print(sgnbServ.exec_server_cmd(time_power,is_print=False).strip())
    
    ###检查频谱仪载波功率
    while True:
        input_power = input("请输入发送的功率值: ")
        if re.match(r"^-?[0-9]+\.?[0-9]*$",input_power):
            break
        else:
            print("功率值格式不对, 请重新输入!!!")
    rx0_power_xdma_list = [
        "xdmaTools 0 0 2b00250 2",
        "xdmaTools 0 0 2b0025c",
        "xdmaTools 0 0 2b0025c",
        "xdmaTools 0 0 2b0025c",
        "xdmaTools 0 0 2b0025c"
    ]
    for rx0_power_xdma in rx0_power_xdma_list:
        rx0_power = sgnbServ.exec_server_cmd(rx0_power_xdma,is_print=False)
        time.sleep(random.randint(1,3))
    rx0_power = re.match(r"0*([1-9A-F]+)",rx0_power).group(1)
    rx0_power = 10*math.log10(int(rx0_power,16)/(2**31))
    rx1_power_xdma_list = [
        "xdmaTools 0 0 2b00250 3",
        "xdmaTools 0 0 2b0025c",
        "xdmaTools 0 0 2b0025c",
        "xdmaTools 0 0 2b0025c",
        "xdmaTools 0 0 2b0025c"
    ]
    for rx1_power_xdma in rx1_power_xdma_list:
        rx1_power = sgnbServ.exec_server_cmd(rx1_power_xdma,is_print=False)
        time.sleep(random.randint(1,3))
    rx1_power = re.match(r"0*([1-9A-F]+)",rx1_power).group(1)
    rx1_power = 10*math.log10(int(rx1_power,16)/(2**31))
    input_power = float(input_power)
    print(f"RX0: {round(input_power - rx0_power,2)}\nRX1: {round(input_power - rx1_power,2)}")
    ### 关闭单音
    # print(sgnbServ.exec_server_cmd("xdmaTools 0 0 2b0016c 0",is_print=False))


def tx0_scattered(sgnbServ: SgnbServ, D2000V_PATH:str, forceinit: bool=False):
    ###初始化8242
    try:
        D2000V_SGNB_PATH = check_d2000v_exist(sgnbServ,D2000V_PATH) 
        check_fpga_info(sgnbServ)
        if forceinit:
            init_8242(sgnbServ,D2000V_SGNB_PATH)
    except ValueError:
        init_8242(sgnbServ,D2000V_SGNB_PATH)
        check_fpga_info(sgnbServ)
    
    ###收发隔离度, tx0 发杂散单音
    time_power_list = [
        "xdmaTools 0 0 2b0016c 1",
        "xdmaTools 0 0 2b00240 0",
        "xdmaTools 0 0 2b00244 0",
        "xdmaTools 0 0 2b00248 0x1fff"
    ]
    for time_power in time_power_list:
        print(sgnbServ.exec_server_cmd(time_power,is_print=False).strip())
    
    ###检查频谱仪载波功率
    input_power = input("请检查频谱仪的杂散信号,bw设置为100k,span设置为600M,搜索最大功率\n"\
                        "请检查中频频率, span设置5M,找到最大功率对应的频偏")
    ### 关闭单音
    # print(sgnbServ.exec_server_cmd("xdmaTools 0 0 2b0016c 0",is_print=False))
    
def tx1_scattered(sgnbServ: SgnbServ, D2000V_PATH:str, forceinit: bool=False):
    ###初始化8242
    try:
        D2000V_SGNB_PATH = check_d2000v_exist(sgnbServ,D2000V_PATH) 
        check_fpga_info(sgnbServ)
        if forceinit:
            init_8242(sgnbServ,D2000V_SGNB_PATH)
    except ValueError:
        init_8242(sgnbServ,D2000V_SGNB_PATH)
        check_fpga_info(sgnbServ)
    
    ###收发隔离度, tx1 发杂散单音
    time_power_list = [
        "xdmaTools 0 0 2b0016c 2",
        "xdmaTools 0 0 2b00240 0",
        "xdmaTools 0 0 2b00244 0",
        "xdmaTools 0 0 2b00248 0x1fff"
    ]
    for time_power in time_power_list:
        print(sgnbServ.exec_server_cmd(time_power,is_print=False).strip())
    
    ###检查频谱仪载波功率
    input_power = input("请检查频谱仪的杂散信号,bw设置为100k,span设置为600M,搜索最大功率\n"\
                        "请检查中频频率, span设置5M,找到最大功率对应的频偏")
    ### 关闭单音
    # print(sgnbServ.exec_server_cmd("xdmaTools 0 0 2b0016c 0",is_print=False))
    
    
if __name__ == '__main__':
    serv_resouce = []

    try:
        sgnbServ_A = SgnbServ(rbc.get_sgnb_cfg(),rbc.get_sgnb_name(0))
        sgnbServ_A.connet_target_sever()
        serv_resouce.append(sgnbServ_A)
        
        ## TX1 发单音,读取RX0和RX1的功率
        # rx_tx_lsolation(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value)
        
        # ### 杂散和频率误差
        # #### TX0 发送单音
        tx0_scattered(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value)
        # #### TX1 发送单音
        # tx1_scattered(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value)

    except KeyboardInterrupt:
        print('Running was interrupted')
    finally:
        print(sgnbServ_A.exec_server_cmd("xdmaTools 0 0 2b0016c 0",is_print=False).strip())
        closed_ssh(serv_resouce)