import time
from module.operation_tsx import *
from module.tshark import *
from config.testData import TsxData
from module import readBasicConfig as rbc
from module.singal import Singal
import re

def pujc_400M_beam2(pujc_cmd,singal_freq):
    serv_resouce = []
    freq_dict = {"4":"120k","3":"15k"}
    mode_dict = {"17":"full_mode","34":"list_mode","51":"control_mode"}
    bw_dict = {'0':"200M","1":"400M"}
    pos_sumnum = {"400M_120k":3334,"400M_15k":26668,"200M_120k":1667,"200M_15k":13334}
    try: 
        # ####启动基站####
        sgnbServ_A = SgnbServ(rbc.get_sgnb_cfg(),rbc.get_sgnb_name(0))
        sgnbServ_A.connet_target_sever()
        serv_resouce.append(sgnbServ_A)
        # # # ####清理log####
        clean_trace(serv_resouce)
        # singal_freq = input("输入当前信号源输出的频率(单位MHZ):")
        # if not singal_freq.replace(".","").isdigit():
        #     raise ValueError("输入的频率不合法")
        # elif "." in singal_freq:
        #     singal_freq = float(singal_freq)
        # else:
        #     singal_freq = int(singal_freq)
        instr = Singal(rbc.get_singal_cfg(0)["signal_ip"])
        instr.singal_pujc_tmp(singal_freq)
        singal_freq = instr.singal_obtain_freq()
        instr.close_connect()
        print(f"当前频率为: {singal_freq} MHz")
        try:
            D2000V_SGNB_PATH = check_d2000v_exist(sgnbServ_A,TsxData.D2000V_PUJC_PATH.value)
            check_fpga_info(sgnbServ_A)
        except ValueError:
            init_8242(sgnbServ_A, D2000V_SGNB_PATH)
            check_fpga_info(sgnbServ_A)
        # # # ####执行SGNB####
        # update_server_time(serv for serv in serv_resouce if serv != amfServ)
        update_server_time(serv_resouce)
        sgnbServ_A.stop_sgnb_process()

        sgnbServ_A.start_sgnb_process(new_Architecture=True,is_copy_cfg=False)
        sgnbServ_A.start_sgnb_scf()
        time.sleep(5)
        print(sgnbServ_A.execuate_scf_cmd(0))
        print(sgnbServ_A.execuate_scf_cmd(0))
        print(sgnbServ_A.execuate_scf_cmd(4))
        sgnb_telnet_server(sgnbServ_A)
        print(sgnbServ_A.execuate_l3_cmd('showCellStatus'))
        print(sgnbServ_A.execuate_l3_cmd('show_beam_pattern'))
        print(sgnbServ_A.execuate_l3_cmd('showPhyCellStatus'))

        # input("等我操作:xxxxxxx")
        print(sgnbServ_A.execuate_l2_cpuA_cmd('settransdebug 0 1'))
        print(sgnbServ_A.execuate_l3_cmd(pujc_cmd))
        print(sgnbServ_A.execuate_l3_cmd('showPhyCellStatus'))
        print(sgnbServ_A.execuate_l3_cmd('showPhyCellStatus'))

        pujc_check_list = [
            "xdmaTools 0 0 02000510",
            "xdmaTools 0 0 02000514",
            "xdmaTools 0 0 02000518"
        ]
        for time_power in pujc_check_list:
            print(sgnbServ_A.exec_server_cmd(time_power,is_print=False))
        result_cellstatus = sgnbServ_A.execuate_l3_cmd('showPhyCellStatus')
        print(result_cellstatus)
        workMode = re.search(r"beam id\[1\].*?workMode\[(.*?)\].*?bw\[(\d+)\].*?onOff.*?\s(\w+)",result_cellstatus)
        trigger = pujc_cmd.split()
        cell_bw = ""
        freq_p = freq_dict[trigger[5]]
        run_mode = mode_dict[trigger[4]]
        if workMode is not None and workMode.group(1) == 'specMonitor'and workMode.group(3) == 'normal':
            cell_bw = bw_dict[workMode.group(2)]
            suffix_name = f"{cell_bw}_{freq_p}_{run_mode}_{singal_freq}"
            result_beam = sgnbServ_A.execuate_l3_cmd('show_beam_pattern')
            print(result_beam)
            print(sgnbServ_A.execuate_l3_cmd('show_BeamWorkModeCommandList 1'))
            print(sgnbServ_A.execuate_l3_cmd('show_BeamWorkModeRunningInfo 1'))
            beamstatus = re.search(r"beam:1.*\nposition index:",result_beam)
            if beamstatus is not None:
                raise(f"频谱监测波束状态异常!!!")
            print("频谱监测功能正常")
        else:
            raise("频谱监测异常!!!")


        print(sgnbServ_A.execuate_phy_cmd('cdt set 1 211/254/16/1/5'))
        sgnbServ_A.capture_pcap(suffix_name)
        # time.sleep(2500)
        time.sleep(3)
        sgnbServ_A.kill_tcpdump()

        ####下载log文件####
        home_file_path = local_log_path(rbc.LOCAL_LOG_PATH, suffix_name)
        download_log(serv_resouce,home_file_path,max_workers=3)
        ### 分析log ####
        subcarrier = pos_sumnum[f"{cell_bw}_{freq_p}"]
        pcap_file = obtain_pcap_file(home_file_path)[0]
        freqStart, subfreq_theory = freqcal(singal_freq, freq_p=int(freq_p[:-1]), subcarrier=subcarrier)
        print()
        print(f"********************信号源发送{singal_freq}, 频谱监测理论监测位置计算************************")
        print(f"理论监测起始位置为freqStart: {freqStart}, subFreqPwr: {subfreq_theory}")
        carrier_sum = obtain_pos_num_max(pcap_file)
        print()
        if carrier_sum != subcarrier:
            raise ValueError(f"获取子载波总数错误, {cell_bw}小区, 理论获取{subcarrier}, 实际获取{carrier_sum}")
        else:
            print(f"获取子载波总数正确, {cell_bw}小区, 理论获取{subcarrier}, 实际获取{carrier_sum}")
        subFreqPwr, pwr = obtain_subfreq_num_max(pcap_file,freqStart)
        print()
        if -1 <= subFreqPwr - subfreq_theory <= 1:
            print(f"实际在freqStart: {freqStart} 下面的subFreqPwr: {subFreqPwr} 检测到的最大功率为{pwr}, 与理论偏差{subFreqPwr-subfreq_theory}")
        else:
            raise ValueError(f"实际在freqStart: {freqStart} 下面的subFreqPwr: {subFreqPwr} 检测到的最大功率为{pwr}, 与理论偏差{subFreqPwr-subfreq_theory}")
    except KeyboardInterrupt:
        print('Running was interrupted')
    finally:
        ####停止基站进程####
        sgnbServ_A.stop_sgnb_process()
        instr = Singal(rbc.get_singal_cfg(0)["signal_ip"])
        instr.close_rf()
        ####清理log####
        clean_trace(serv_resouce)
        closed_ssh(serv_resouce)

if __name__ == '__main__':
    # 120k全景扫描模式
    pujc_400M_beam2('addBeamTask 1 90 17 4 1 1 1',"2060MHZ")
    # pujc_400M_beam2('addBeamTask 1 90 17 4 1 1 1',"2251MHZ")
    # pujc_400M_beam2('addBeamTask 1 90 17 4 1 1 1',"2440MHZ")
    # # 120k频点控守模式
    # pujc_400M_beam2('addBeamTask 1 90 34 4 1 1 1',"2060MHZ")
    # pujc_400M_beam2('addBeamTask 1 90 34 4 1 1 1',"2251MHZ")
    # pujc_400M_beam2('addBeamTask 1 90 34 4 1 1 1',"2440MHZ")
    # # 120k频点控守模式
    # pujc_400M_beam2('addBeamTask 1 90 51 4 1 1 1',"2060MHZ")
    # pujc_400M_beam2('addBeamTask 1 90 51 4 1 1 1',"2251MHZ")
    # pujc_400M_beam2('addBeamTask 1 90 51 4 1 1 1',"2440MHZ")
    # # 15k全景扫描模式
    # pujc_400M_beam2('addBeamTask 1 90 17 3 1 1 1',"2060MHZ")
    # pujc_400M_beam2('addBeamTask 1 90 17 3 1 1 1',"2251MHZ")
    # pujc_400M_beam2('addBeamTask 1 90 17 3 1 1 1',"2440MHZ")
    # # 15k频点控守模式
    # pujc_400M_beam2('addBeamTask 1 90 34 3 1 1 1',"2060MHZ")
    # pujc_400M_beam2('addBeamTask 1 90 34 3 1 1 1',"2251MHZ")
    # pujc_400M_beam2('addBeamTask 1 90 34 3 1 1 1',"2440MHZ")
    # # 15k频点控守模式
    # pujc_400M_beam2('addBeamTask 1 90 51 3 1 1 1',"2060MHZ")
    # pujc_400M_beam2('addBeamTask 1 90 51 3 1 1 1',"2251MHZ")
    # pujc_400M_beam2('addBeamTask 1 90 51 3 1 1 1',"2440MHZ")
    