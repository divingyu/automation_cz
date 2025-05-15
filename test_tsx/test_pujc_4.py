import time
from common.operation_tsx import *
from common.tshark import *
from conf.testData import TsxData
from common import readBasicConfig as rbc
from common.rs_signal import Signal
from func_timeout import func_set_timeout, FunctionTimedOut
import re
import pytest
import logging

def timeout_decorator(timeout):
    def wrapper(func):
        def inner(*args, **kwargs):
            try:
                func_set_timeout(timeout)(func)(*args, **kwargs)
            except FunctionTimedOut:
                raise TimeoutError(f"Function {func.__name__} timed out after {timeout} seconds")
        return inner
    return wrapper


class TestPujc():
    serv_resouce = []
    freq_dict = {"4":"120k","3":"15k"}
    mode_dict = {"1":"full_mode","2":"list_mode","3":"control_mode"}
    # mode_dict = {"17":"full_mode","34":"list_mode","51":"control_mode"}
    bw_dict = {'0':"200M","1":"400M"}
    pos_sumnum = {"400M_120k":3334,"400M_15k":26668,"200M_120k":1667,"200M_15k":13334}
    suffix_name = ""
    marking = False
    def setup_method(self):
        self.sgnbServ_A = SgnbServ(rbc.get_sgnb_cfg(),rbc.get_sgnb_name(0))
        self.sgnbServ_A.connet_target_sever()
        self.serv_resouce.append(self.sgnbServ_A)
        update_server_time(self.serv_resouce)
        self.sgnbServ_A.stop_sgnb_process()
        clean_trace(self.serv_resouce)

    def teardown_method(self):
        ####停止基站进程####
        self.sgnbServ_A.stop_sgnb_process()
        instr = Singal(rbc.get_singal_cfg(0)["signal_ip"])
        instr.close_rf()
        if not self.marking:
            home_file_path = local_log_path(rbc.LOCAL_LOG_PATH, self.suffix_name)
            download_log(self.serv_resouce,home_file_path,max_workers=3)
        ####清理log####
        clean_trace(self.serv_resouce)
        closed_ssh(self.serv_resouce)
        self.serv_resouce[:] = []
        self.marking = False

    # @pytest.mark.parametrize("pujc_cmd,singal_freq",[
    #     ("addBeamTask 1 0 90 17 4 1 1 1","2060MHZ"),("addBeamTask 1 0 90 17 4 1 1 1","2251MHZ"),("addBeamTask 1 0 90 17 4 1 1 1","2440MHZ"),
    #     ("addBeamTask 1 0 90 34 4 1 1 1","2060MHZ"),("addBeamTask 1 0 90 34 4 1 1 1","2251MHZ"),("addBeamTask 1 0 90 34 4 1 1 1","2440MHZ"),
    #     ("addBeamTask 1 0 90 51 4 1 1 1","2060MHZ"),("addBeamTask 1 0 90 51 4 1 1 1","2251MHZ"),("addBeamTask 1 0 90 51 4 1 1 1","2440MHZ"),
    #     ("addBeamTask 1 0 90 17 3 1 1 1","2060MHZ"),("addBeamTask 1 0 90 17 3 1 1 1","2251MHZ"),("addBeamTask 1 0 90 17 3 1 1 1","2440MHZ"),
    #     ("addBeamTask 1 0 90 34 3 1 1 1","2060MHZ"),("addBeamTask 1 0 90 34 3 1 1 1","2251MHZ"),("addBeamTask 1 0 90 34 3 1 1 1","2440MHZ"),
    #     ("addBeamTask 1 0 90 51 3 1 1 1","2060MHZ"),("addBeamTask 1 0 90 51 3 1 1 1","2251MHZ"),("addBeamTask 1 0 90 51 3 1 1 1","2440MHZ")
    # ])
    # @pytest.mark.parametrize("pujc_cmd,singal_freq",[
    #     ("addBeamTask 1 0 90 1 4 1 1 1","2060MHZ"),("addBeamTask 1 0 90 1 4 1 1 1","2251MHZ"),("addBeamTask 1 0 90 1 4 1 1 1","2440MHZ"),
    #     ("addBeamTask 1 0 90 2 4 1 1 1","2060MHZ"),("addBeamTask 1 0 90 2 4 1 1 1","2251MHZ"),("addBeamTask 1 0 90 2 4 1 1 1","2440MHZ"),
    #     ("addBeamTask 1 0 90 3 4 1 1 1","2060MHZ"),("addBeamTask 1 0 90 3 4 1 1 1","2251MHZ"),("addBeamTask 1 0 90 3 4 1 1 1","2440MHZ"),
    #     ("addBeamTask 1 0 90 1 3 1 1 1","2060MHZ"),("addBeamTask 1 0 90 1 3 1 1 1","2251MHZ"),("addBeamTask 1 0 90 1 3 1 1 1","2440MHZ"),
    #     ("addBeamTask 1 0 90 2 3 1 1 1","2060MHZ"),("addBeamTask 1 0 90 2 3 1 1 1","2251MHZ"),("addBeamTask 1 0 90 2 3 1 1 1","2440MHZ"),
    #     ("addBeamTask 1 0 90 3 3 1 1 1","2060MHZ"),("addBeamTask 1 0 90 3 3 1 1 1","2251MHZ"),("addBeamTask 1 0 90 3 3 1 1 1","2440MHZ")
    # ])
    @pytest.mark.parametrize("pujc_cmd,singal_freq",[
        ("addBeamTask 1 0 90 1 4 1 1 1","2160MHZ"),("addBeamTask 1 0 90 1 4 1 1 1","2251MHZ"),("addBeamTask 1 0 90 1 4 1 1 1","2340MHZ"),
        ("addBeamTask 1 0 90 2 4 1 1 1","2160MHZ"),("addBeamTask 1 0 90 2 4 1 1 1","2251MHZ"),("addBeamTask 1 0 90 2 4 1 1 1","2340MHZ"),
        ("addBeamTask 1 0 90 3 4 1 1 1","2160MHZ"),("addBeamTask 1 0 90 3 4 1 1 1","2251MHZ"),("addBeamTask 1 0 90 3 4 1 1 1","2340MHZ"),
        ("addBeamTask 1 0 90 1 3 1 1 1","2160MHZ"),("addBeamTask 1 0 90 1 3 1 1 1","2251MHZ"),("addBeamTask 1 0 90 1 3 1 1 1","2340MHZ"),
        ("addBeamTask 1 0 90 2 3 1 1 1","2160MHZ"),("addBeamTask 1 0 90 2 3 1 1 1","2251MHZ"),("addBeamTask 1 0 90 2 3 1 1 1","2340MHZ"),
        ("addBeamTask 1 0 90 3 3 1 1 1","2160MHZ"),("addBeamTask 1 0 90 3 3 1 1 1","2251MHZ"),("addBeamTask 1 0 90 3 3 1 1 1","2340MHZ")
    ])
    @pytest.mark.cycle
    @pytest.mark.flaky(reruns=3, reruns_delay=5)
    def test_pujc_400M_beam2(self,pujc_cmd,singal_freq):
        try: 
            instr = Singal(rbc.get_singal_cfg(0)["signal_ip"])
            instr.singal_pujc_tmp(singal_freq)
            singal_freq = instr.singal_obtain_freq()
            instr.close_connect()
            print(f"当前频率为: {singal_freq} MHz")
            try:
                D2000V_SGNB_PATH = check_d2000v_exist(self.sgnbServ_A,TsxData.D2000V_PUJC_PATH.value)
                check_fpga_info(self.sgnbServ_A)
            except ValueError:
                init_8242(self.sgnbServ_A, D2000V_SGNB_PATH)
                check_fpga_info(self.sgnbServ_A)
            # # # ####执行SGNB####
            self.sgnbServ_A.start_sgnb_process(new_Architecture=True,is_copy_cfg=False)
            self.sgnbServ_A.start_sgnb_scf()
            time.sleep(5)
            print(self.sgnbServ_A.execuate_scf_cmd(0))
            print(self.sgnbServ_A.execuate_scf_cmd(0))
            print(self.sgnbServ_A.execuate_scf_cmd(4))
            sgnb_telnet_server(self.sgnbServ_A)
            print(self.sgnbServ_A.execuate_l3_cmd('showCellStatus'))
            print(self.sgnbServ_A.execuate_l3_cmd('show_beam_pattern'))
            print(self.sgnbServ_A.execuate_l3_cmd('showPhyCellStatus'))

            print(self.sgnbServ_A.execuate_l2_cpuA_cmd('settransdebug 0 1'))
            print(self.sgnbServ_A.execuate_l3_cmd('showPhyCellStatus'))
            print(self.sgnbServ_A.execuate_l3_cmd(pujc_cmd))
            print(self.sgnbServ_A.execuate_l3_cmd('showPhyCellStatus'))
            print(self.sgnbServ_A.execuate_l3_cmd('showPhyCellStatus'))

            pujc_check_list = [
                "xdmaTools 0 0 02000510",
                "xdmaTools 0 0 02000514",
                "xdmaTools 0 0 02000518"
            ]
            for time_power in pujc_check_list:
                print(self.sgnbServ_A.exec_server_cmd(time_power,is_print=False))
            result_cellstatus = self.sgnbServ_A.execuate_l3_cmd('showPhyCellStatus')
            print(result_cellstatus)
            workMode = re.search(r"beam id\[1\].*?workMode\[(.*?)\].*?bw\[(\d+)\].*?onOff.*?\s(\w+)",result_cellstatus)
            trigger = pujc_cmd.split()
            cell_bw = ""
            freq_p = self.freq_dict[trigger[5]]
            run_mode = self.mode_dict[trigger[4]]
            if workMode is not None and workMode.group(1) == 'specMonitor'and workMode.group(3) == 'normal':
                cell_bw = self.bw_dict[workMode.group(2)]
                self.suffix_name = f"{cell_bw}_{freq_p}_{run_mode}_{singal_freq}"
                result_beam = self.sgnbServ_A.execuate_l3_cmd('show_beam_pattern')
                print(result_beam)
                print(self.sgnbServ_A.execuate_l3_cmd('show_BeamWorkModeCommandList 1'))
                print(self.sgnbServ_A.execuate_l3_cmd('show_BeamWorkModeRunningInfo 1'))
                beamstatus = re.search(r"beam:1.*\nposition index:",result_beam)
                if beamstatus is not None:
                    raise(f"频谱监测波束状态异常!!!")
                print("频谱监测功能正常")
            else:
                raise("频谱监测异常!!!")
            self.marking = True
            print(self.sgnbServ_A.execuate_phy_cmd('cdt set 1 211/254/16/1/5'))
            logging.info(self.suffix_name)
            self.sgnbServ_A.capture_pcap(self.suffix_name)
            time.sleep(3)
            self.sgnbServ_A.kill_tcpdump()

            ####下载log文件####
            home_file_path = local_log_path(rbc.LOCAL_LOG_PATH, self.suffix_name)
            download_log(self.serv_resouce,home_file_path,max_workers=3)
            ### 分析log ####
            subcarrier = self.pos_sumnum[f"{cell_bw}_{freq_p}"]
            
            pcap_file = obtain_pcap_file(home_file_path)[0]
            freqStart, subfreq_theory = freqcal(singal_freq, freq_p=int(freq_p[:-1]), subcarrier=subcarrier)
            print()
            print(f"********************信号源发送{singal_freq}, 频谱监测理论监测位置计算************************")
            logging.info(f"理论监测起始位置为freqStart: {freqStart}, subFreqPwr: {subfreq_theory}")
            carrier_sum = obtain_pos_num_max(pcap_file)
            print()
            if carrier_sum != subcarrier:
                raise ValueError(f"获取子载波总数错误, {cell_bw}小区, 理论获取{subcarrier}, 实际获取{carrier_sum}")
            else:
                logging.info(f"获取子载波总数正确, {cell_bw}小区, 理论获取{subcarrier}, 实际获取{carrier_sum}")
            subFreqPwr, pwr = obtain_subfreq_num_max(pcap_file,freqStart)
            print()
            if -1 <= subFreqPwr - subfreq_theory <= 1:
                logging.info(f"实际在freqStart: {freqStart} 下面的subFreqPwr: {subFreqPwr} 检测到的最大功率为{pwr}, 与理论偏差{subFreqPwr-subfreq_theory}")
            else:
                raise ValueError(f"实际在freqStart: {freqStart} 下面的subFreqPwr: {subFreqPwr} 检测到的最大功率为{pwr}, 与理论偏差{subFreqPwr-subfreq_theory}")
        except Exception as e:
            print(e)
            raise e