from module.operation_tsx import *
from module import readBasicConfig as rbc
from config.testData import TsxData

def outputpower_evm_ptd_F1(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, forceinit: bool=False):
    # ###初始化8242
    try:
        D2000V_SGNB_PATH = check_d2000v_exist(sgnbServ,D2000V_PATH) 
        check_fpga_info(sgnbServ)
        if forceinit:
            init_8242(sgnbServ,D2000V_SGNB_PATH)
    except ValueError:
        init_8242(sgnbServ,D2000V_SGNB_PATH)
        check_fpga_info(sgnbServ)
    ###F1 输出功率, EVM, 平坦度验证测试
    GTESTPHT = check_gtestphy_exist(sgnbServ, GTESTPHY_PATH)
    kill_gtestphy_ps(sgnbServ)
    print("复位CPU")
    fucmd = "xdmaTools 0 0 0x01000800 1;xdmaTools 0 0 0x01000800 0;xdmaTools 0 0 02a00004 1;xdmaTools 0 0 02a00004"
    print(sgnbServ.exec_server_cmd(fucmd,is_print=False).strip())
    gtestps = start_gtestphy(sgnbServ, GTESTPHT, "5 20000 0 1")
    
    ###F1 时域功控
    time_cmd = "xdmaTools 0 0 2500104 fc\nxdmaTools 0 0 2500108 3800\nxdmaTools 0 0 2600104 fb\nxdmaTools 0 0 2600108 4600\n"
    sgnbServ.exec_server_cmd(time_cmd,is_print=False).strip()
    print(sgnbServ.exec_server_cmd(time_cmd,is_print=False).strip())
    
    ###检查频谱仪载波功率
    input("测试 CPU1(F1) EVM, 中频最大输出电平, 中频平坦度 的数据")
    
    ### 关闭测试
    # kill_gtestphy_ps(sgnbServ)

def outputpower_evm_ptd_F2(sgnbServ: SgnbServ, D2000V_PATH:str, GTESTPHY_PATH:str, forceinit: bool=False):
    ###初始化8242
    try:
        D2000V_SGNB_PATH = check_d2000v_exist(sgnbServ,D2000V_PATH) 
        check_fpga_info(sgnbServ)
        if forceinit:
            init_8242(sgnbServ,D2000V_SGNB_PATH)
    except ValueError:
        init_8242(sgnbServ,D2000V_SGNB_PATH)
        check_fpga_info(sgnbServ)

    ###F1 输出功率, EVM, 平坦度验证测试
    GTESTPHT = check_gtestphy_exist(sgnbServ, GTESTPHY_PATH)
    print("复位CPU")
    fucmd = "xdmaTools 0 0 0x01000800 1;xdmaTools 0 0 0x01000800 0;xdmaTools 0 0 02a00004 1;xdmaTools 0 0 02a00004"
    print(sgnbServ.exec_server_cmd(fucmd,is_print=False).strip())
    kill_gtestphy_ps(sgnbServ)
    gtestps = start_gtestphy(sgnbServ, GTESTPHT, "5 20000 0 1")
    
    ###F2 时域功控
    time_cmd = "xdmaTools 0 0 2500104 fc;xdmaTools 0 0 2500108 3900\nxdmaTools 0 0 2600104 fc\nxdmaTools 0 0 2600108 2500\nxdmaTools 0 0 200002c 2\nxdmaTools 0 0 2000030 3\n"
    sgnbServ.exec_server_cmd(time_cmd,is_print=False).strip()
    print(sgnbServ.exec_server_cmd(time_cmd,is_print=False).strip())
    
    ###检查频谱仪载波功率
    input("测试 CPU2(F2) EVM, 中频最大输出电平, 中频平坦度 的数据")
    
    ### 关闭子载波测试
    # kill_gtestphy_ps(sgnbServ)

if __name__ == '__main__':
    serv_resouce = []

    try:
        sgnbServ_A = SgnbServ(rbc.get_sgnb_cfg(),rbc.get_sgnb_name(0))
        sgnbServ_A.connet_target_sever()
        serv_resouce.append(sgnbServ_A)
        
        ### 星载1输出功率, EVM, 平坦度验证
        #### F1-1为cpu1的波束1的TX0, 200M波束; F1-2为cpu1的波束2的TX1, 400M波束. 测试F1-1, F1-2
        outputpower_evm_ptd_F1(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value,TsxData.GTESTPHT_F1_TX_EVM_MCS16_PATH.value)
        #### F2-1为cpu2的波束1的TX0, 200M波束; F2-2为cpu2的波束2的TX1, 200M波束. 测试F2-1, F2-2
        # outputpower_evm_ptd_F2(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value,TsxData.GTESTPHT_F2_TX_EVM_MCS16_PATH.value)

    except KeyboardInterrupt:
        print('Running was interrupted')
    finally:
        kill_gtestphy_ps(sgnbServ_A)
        closed_ssh(serv_resouce)