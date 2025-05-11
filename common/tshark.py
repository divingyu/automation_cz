import os
import pyshark
import tarfile
from conf.testData import TsxData


def obtain_pcap_file(pcap_path):
    pcap_files = [
        os.path.join(root, file)
        for root, _, files in os.walk(pcap_path)
        for file in files
        if file.endswith(('.pcap', '.pcapng'))
    ]
    if not pcap_files:
        tar_file = next(
                (os.path.join(root, file) for root, _, files in os.walk(pcap_path) for file in files if
                 file == "sgnb_pcap.tar.gz"),
                None
        )
        if tar_file:
            with tarfile.open(tar_file, 'r:gz') as tar:
                tar.extractall(path = os.path.dirname(tar_file), filter = 'data')
                pcap_files = [
                    os.path.join(os.path.dirname(tar_file), extracted_file)
                    for extracted_file in os.listdir(os.path.dirname(tar_file))
                    if extracted_file.endswith(('.pcap', '.pcapng'))
                ]
    return pcap_files


def freqcal(singal_freq, freq_p = 15, subcarrier = 26668, center_freq = 2250):
    center_freq_p = int(subcarrier / 2 + 1)
    offset_p = round((singal_freq * 1000 - center_freq * 1000) / freq_p)
    theory_p = center_freq_p + offset_p
    freqStart = int(theory_p / 512) * 512
    subfreq = int(theory_p - freqStart)
    return freqStart, subfreq


def obtain_freqstart_set(pcap_file):
    with pyshark.FileCapture(pcap_file, tshark_path = TsxData.TSHARK_PATH.value, display_filter = "data") as cap:
        freqstart_set = set()
        for pcap in cap:
            for layer in pcap.layers:
                if "freqstart" in layer.field_names:
                    freqstart_value = int(layer.get_field("freqstart"))
                    if freqstart_value in freqstart_set:
                        return freqstart_set
                    freqstart_set.add(freqstart_value)
        return freqstart_set


def obtain_pos_num_max(pcap_file):
    max_freqstart = max(obtain_freqstart_set(pcap_file))
    number = 0
    with pyshark.FileCapture(pcap_file, tshark_path = TsxData.TSHARK_PATH.value,
                             display_filter = f"freqStart == {max_freqstart}") as cap:
        for pcap in cap:
            for layer in pcap.layers:
                for name in layer.field_names:
                    if 'my_protocol_int16_' in name:
                        if layer.get_field(name) != "0":
                            number += 1
                            continue
                        return number + max_freqstart


def obtain_subfreq_num_max(pcap_file, freqstart):
    with pyshark.FileCapture(pcap_file, tshark_path = TsxData.TSHARK_PATH.value,
                             display_filter = f"freqStart == {freqstart}") as cap:
        number = 1
        subFreqPwr = {}
        for pcap in cap:
            for layer in pcap.layers:
                for name in layer.field_names:
                    if 'my_protocol_int16_' in name:
                        split_pos = name.split('_')[-1]
                        subFreqPwr[int(split_pos)] = int(layer.get_field(name))
                        number += 1
                        if number > 512:
                            # max_key = max(subFreqPwr, key=subFreqPwr.get)
                            return find_max_with_key(subFreqPwr)


def find_max_with_key(d):
    non_zero_items = {k:v for k, v in d.items() if v != 0}
    if not non_zero_items:
        return None, None
    sorted_items = sorted(non_zero_items.items(), key = lambda x:x[1])

    if len(sorted_items) >= 2:
        return sorted_items[-1][0], sorted_items[-1][1]
    else:
        return sorted_items[0][0], sorted_items[0][1]


if __name__ == '__main__':
    # pcap_path = r'C:\Users\Lenovo\Desktop\tsx_auto\log\2025-04-02_10_37_57_15k_control_mode_2060\d2000v_2025-04
    # -02_10_37_57'
    pcap_path = r'C:\Users\Lenovo\Desktop\tsx_auto\log\2025-04-10_14_21_02_400M_120k_full_mode_2440'
    # sub = float(input("请检查频谱仪的连接是否正常"))
    freqStart, subfreq_theory = freqcal(2440, freq_p = 120, subcarrier = 3334)
    print(f"理论信号搜索到的位置在freqStart:{freqStart} 里面的subfreq {subfreq_theory}")
    pcap_file = obtain_pcap_file(pcap_path)
    print(pcap_file)
    # print (obtain_pos_num_max(pcap_file))
    print(obtain_subfreq_num_max(pcap_file[0], freqStart))