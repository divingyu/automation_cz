"""
Company            :
Create Date        : 2025-01-24 14:13:30
Engineer           : You Yuling
Target Devices     : basic config file
Tool Versions      : v_1.0
Description        : obtain config method
Revision           : LastEditTime
"""
import os
import json


def __obtain_basic_cfg():
    __filename = 'basic_config.json'
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    global __filepath
    __filepath = os.path.join(parent_dir, 'config', __filename)
    with open(__filepath, 'r') as file:
        return json.load(file)


__cfg_data = __obtain_basic_cfg()
LOCAL_LOG_PATH = __cfg_data['local_log_path']
__sgnb_list = []
__ue_list = []
__amf_list = []
__jump_list = []
__ftp_list = []
__singal_list = []


def __get__sgnb_list():
    if __sgnb_list != []:
        return
    try:
        for sgnb in __cfg_data['sgnb']:
            __sgnb_list.append(sgnb)
    except Exception as e:
        raise KeyError(f"Please check the basic config file sgnb field ! {e}")


def get_sgnb_len() -> int:
    if __sgnb_list == []:
        __get__sgnb_list()
    return len(__sgnb_list)


def get_sgnb_name(index: int) -> str:
    if __sgnb_list == []:
        __get__sgnb_list()
    if index >= len(__sgnb_list):
        index = len(__sgnb_list) - 1
    return __sgnb_list[index]


def get_sgnb_cfg(index: int = 0) -> dict:
    if __sgnb_list == []:
        __get__sgnb_list()
    return __cfg_data['sgnb'][get_sgnb_name(index)]


def __get__ue_list():
    if __ue_list != []:
        return
    try:
        for ue in __cfg_data['ue']:
            __ue_list.append(ue)
    except Exception as e:
        raise KeyError(f"Please check the basic config file ue field ! {e}")


def get_ue_len() -> int:
    if __ue_list == []:
        __get__ue_list()
    return len(__ue_list)


def get_ue_name(index: int) -> str:
    if __ue_list == []:
        __get__ue_list()
    if index >= len(__ue_list):
        index = len(__ue_list) - 1
    return __ue_list[index]


def get_ue_mac_cfg(index: int = 0) -> dict:
    if __ue_list == []:
        __get__ue_list()
    return __cfg_data['ue'][get_ue_name(index)]['ue_mac']


def get_ue_phy_cfg(index: int = 0) -> dict:
    if __ue_list == []:
        __get__ue_list()
    return __cfg_data['ue'][get_ue_name(index)]['ue_phy']


def __get__amf_list():
    if __amf_list != []:
        return
    try:
        for amf in __cfg_data['amf']:
            __amf_list.append(amf)
    except Exception as e:
        raise KeyError(f"Please check the basic config file amf field ! {e}")


def get_amf_len() -> int:
    if __amf_list == []:
        __get__amf_list()
    return len(__amf_list)


def get_amf_name(index: int) -> str:
    if __amf_list == []:
        __get__amf_list()
    if index >= len(__amf_list):
        index = len(__amf_list) - 1
    return __amf_list[index]


def get_amf_cfg(index: int = 0) -> dict:
    if __amf_list == []:
        __get__amf_list()
    return __cfg_data['amf'][get_amf_name(index)]


def __get__jump_list():
    if __jump_list != []:
        return
    try:
        for jump in __cfg_data['jump']:
            __jump_list.append(jump)
    except Exception as e:
        raise KeyError(f"Please check the basic config file jump field ! {e}")


def get_jump_len() -> int:
    if __jump_list == []:
        __get__jump_list()
    return len(__jump_list)


def get_jump_name(index: int) -> str:
    if __jump_list == []:
        __get__jump_list()
    if index >= len(__jump_list):
        index = len(__jump_list) - 1
    return __jump_list[index]


def get_jump_cfg(index: int = 0) -> dict:
    if __jump_list == []:
        __get__jump_list()
    return __cfg_data['jump'][get_jump_name(index)]


def __get__ftp_list():
    if __ftp_list != []:
        return
    try:
        for ftp in __cfg_data['ftp']:
            __ftp_list.append(ftp)
    except Exception as e:
        raise KeyError(f"Please check the basic config file ftp field ! {e}")


def get_ftp_len() -> int:
    if __ftp_list == []:
        __get__ftp_list()
    return len(__ftp_list)


def get_ftp_name(index: int) -> str:
    if __ftp_list == []:
        __get__ftp_list()
    if index >= len(__ftp_list):
        index = len(__ftp_list) - 1
    return __ftp_list[index]


def get_ftp_cfg(index: int = 0) -> dict:
    if __ftp_list == []:
        __get__ftp_list()
    return __cfg_data['ftp'][get_ftp_name(index)]


def __get__singal_list():
    if __singal_list != []:
        return
    try:
        for singal in __cfg_data['singal']:
            __singal_list.append(singal)
    except Exception as e:
        raise KeyError(f"Please check the basic config file ftp field ! {e}")


def get_singal_len() -> int:
    if __singal_list == []:
        __get__singal_list()
    return len(__singal_list)


def get_singal_name(index: int) -> str:
    if __singal_list == []:
        __get__singal_list()
    if index >= len(__singal_list):
        index = len(__singal_list) - 1
    return __singal_list[index]


def get_singal_cfg(index: int = 0) -> dict:
    if __singal_list == []:
        __get__singal_list()
    return __cfg_data['singal'][get_singal_name(index)]


def modify_basic_cfg():
    with open(__filepath, 'w') as file:
        json.dump(__cfg_data, file, indent = 4)

# if __name__ == '__main__':
# print(get_ue_mac_cfg(1))
# print(get_ue_len())
# print(get_ue_phy_cfg(1))
# print(get_sgnb_cfg(0)['exec_path'])
# get_sgnb_cfg(0)['exec_path'] = '/home/sgnb'
# modify_basic_cfg()
# print(get_sgnb_len())
# print(get_amf_cfg(0))
# print(get_amf_len())
# print(get_jump_cfg())
# print(get_jump_len())
# print(get_ftp_cfg())
# print(get_ftp_len())
# print(LOCAL_LOG_PATH)