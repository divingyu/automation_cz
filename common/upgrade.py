"""
Company            :
Create Date        : 2025-01-25 21:03:41
Engineer           : You Yuling
Target Devices     : upgrade sgnb & ue version
Tool Versions      : v_1.0
Description        : upgrade sgnb & ue version
Revision           : LastEditTime
"""
import os
import re
import json
import tarfile
import xml.etree.ElementTree as et


def uncompress_tar_gz_file(file_path: str) -> str:
    """
    Uncompress a .tar.gz file to a directory.
    Args:
        file_path (str): The path to the .tar.gz file to be uncompressed.
    Returns:
        str: The path to the directory where the contents were extracted.
    """

    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return ''

    if '.'.join(file_path.split('.')[-2:]) != 'tar.gz':
        raise AttributeError("not a .tar.gz file")

    with tarfile.open(file_path, 'r:gz') as tar:
        members = tar.getmembers()
        top_level_dirs = {member.name.split('/')[0] for member in members}
        if len(top_level_dirs) == 1:
            output_dir = os.path.dirname(file_path)
            tar.extractall(path = output_dir, filter = 'data')
            output_dir = f"{output_dir}\\{top_level_dirs.pop()}"
        else:
            output_dir = os.path.splitext(os.path.splitext(file_path)[0])[0]
            tar.extractall(path = output_dir, filter = 'data')

    print(f"Extracted to {output_dir}")
    return output_dir


def find_config_file(file_path: str, filename_cfg: str) -> str:
    """
    Searches for a configuration file within a specified directory and its subdirectories.
    Args:
        file_path (str): The path to the directory where the search should begin.
        filename_cfg (str): The name of the configuration file to search for.
    Returns:
        str: The full path to the configuration file if found, otherwise None.
        """

    if not os.path.exists(file_path):
        print(f"Folder {file_path} does not exist.")
        return ''

    for root, dirs, files in os.walk(file_path):
        if filename_cfg in files:
            config_file_path = os.path.join(root, filename_cfg)
            return config_file_path
    print(f"Config file {filename_cfg} not found in {file_path}")
    return ''


def obtain_cfg_json(filename):
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    __filepath = os.path.join(parent_dir, 'conf', filename)
    with open(__filepath, 'r', encoding = 'utf-8') as file:
        return json.load(file)


def modify_xml_file(file_full_path: str, cfg_jsons: dict) -> None:
    """
    Modifies an XML file based on the provided configuration JSONs.
    Args:
        file_full_path (str): The full path to the XML file to be modified.
        cfg_jsons (dict): A dictionary containing configuration JSONs. Each JSON
                            should have a 'pattern' key to find XML elements and
                            other keys to specify the modifications. The 'description'
                            key, if present, will be ignored.
    Returns:
        None
    """

    if not os.path.exists(file_full_path):
        print(f"File {file_full_path} does not exist.")
        return
    else:
        backup_path = file_full_path + ".bak"
        with open(file_full_path, 'rb') as original_file:
            with open(backup_path, 'wb') as backup_file:
                backup_file.write(original_file.read())

    tree = et.parse(file_full_path)
    root = tree.getroot()

    for cfg in cfg_jsons:
        pattern = cfg['pattern']
        del cfg['pattern']
        if cfg.get('description') is not None:
            del cfg['description']
        for i, elem in enumerate(root.findall(pattern)):
            for value in (cfg.values()):
                if re.match(r"^all$", str(value['position']), re.I) is not None:
                    elem.text = value['value']
                elif value['position'] == i:
                    elem.text = value['value']
    with open(file_full_path, 'wb') as file:
        tree.write(file, encoding = 'utf-8', xml_declaration = True)


def find_xml_file_text(file_full_path: str, pattern: str) -> None:
    if not os.path.exists(file_full_path):
        print(f"File {file_full_path} does not exist.")
        return
    tree = et.parse(file_full_path)
    root = tree.getroot()

    for elem in root.findall(pattern):
        print(elem.text)


def get_deepest_keys(d, parent_key = '', sep = '.'):
    """
    Recursively finds the deepest keys in a nested dictionary or list.
    Args:
        d (dict or list): The dictionary or list to search.
        parent_key (str): The base key string for recursion.
        sep (str): The separator between keys.
    Returns:
        list: A list of tuples containing the deepest keys and their values.
    """
    items = []
    if isinstance(d, dict):
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, (dict, list)):
                items.extend(get_deepest_keys(v, new_key, sep = sep))
            else:
                items.append((new_key, v))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            new_key = f"{parent_key}{sep}{i}" if parent_key else i
            if isinstance(v, (dict, list)):
                items.extend(get_deepest_keys(v, new_key, sep = sep))
            else:
                items.append((new_key, v))
    return items


def update_json(base, modify):
    if isinstance(modify, dict):
        for key, value in modify.items():
            if key in base:
                if isinstance(value, (dict, list)):
                    update_json(base[key], value)
                else:
                    base[key] = value
            else:
                base[key] = value
    elif isinstance(modify, list):
        for i, value in enumerate(modify):
            if i < len(base):
                if isinstance(value, (dict, list)):
                    update_json(base[i], value)
                else:
                    base[i] = value
            else:
                base.append(value)


def modify_json_file(file_full_path: str, cfg_jsons: dict) -> None:
    """
    Modifies a JSON file by updating its contents with the provided configuration JSON.
    Args:
        file_full_path (str): The full path to the JSON file to be modified.
        cfg_jsons (dict): A dictionary containing the configuration JSON data to update
                            the original JSON file.
    Returns:
        None
    """
    if not os.path.exists(file_full_path):
        print(f"File {file_full_path} does not exist.")
        return
    else:
        backup_path = file_full_path + ".bak"
        with open(file_full_path, 'r') as original_file:
            with open(backup_path, 'w', newline = '') as backup_file:
                backup_file.write(original_file.read())

    with open(file_full_path, 'r') as file:
        json_data = json.load(file)

    update_json(json_data, cfg_jsons)

    with open(file_full_path, 'w', newline = '') as file:
        json.dump(json_data, file, indent = 4)


def organize_compress_sgnb_documents(version_path: str, compress_filename: str = '') -> str:
    """
    Organizes and compresses the S-gNB documents into a .tar.gz file.
    Args:
        :param version_path: The path to the directory containing the S-gNB documents.
        :param compress_filename:
    """
    if compress_filename == '':
        compress_filename = os.path.basename(version_path).split('.')[-1]
    version_path = f"{version_path}\\protocol_stack"
    if not os.path.exists(version_path):
        print(f"Directory {version_path} does not exist.")
        return ''

    print(f"Compressing {version_path} into {compress_filename}.tar.gz")
    output_filename = f"{os.path.dirname(version_path)}\\{compress_filename}.tar.gz"
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(version_path, arcname = compress_filename)

    print(f"Compressed to {output_filename}")
    return output_filename


def organize_compress_ue_documents(version_path: str, subdirectory: str) -> str:
    """
    Organizes and compresses the UE MAC documents into a .tar.gz file.
    Args:
        :param version_path: The path to the directory containing the UE documents.
        :param subdirectory:
    """
    compress_filename = f"{subdirectory}_{version_path.split('.')[-1]}"
    version_path = f"{version_path}\\{subdirectory}"
    if not os.path.exists(version_path):
        print(f"Directory {version_path} does not exist.")
        return ''

    print(f"Compressing {version_path} into {compress_filename}.tar.gz")
    output_filename = f"{os.path.dirname(version_path)}\\{compress_filename}.tar.gz"
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(version_path, arcname = compress_filename)

    print(f"Compressed to {output_filename}")
    return output_filename


def compress_folder(folder_path: str) -> str:
    """
    Compresses a directory into a .tar.gz file.
    Args:
        folder_path (str): The path to the directory to be compressed.
    """
    if not os.path.exists(folder_path):
        print(f"Directory {folder_path} does not exist.")
        return ''
    compress_filename = os.path.basename(folder_path)

    print(f"Compressing {folder_path} into {compress_filename}.tar.gz")
    output_filename = f"{os.path.dirname(folder_path)}\\{compress_filename}.tar.gz"
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(folder_path, arcname = compress_filename)

    print(f"Compressed to {output_filename}")
    return output_filename


if __name__ == '__main__':
    # filepath = r'C:\Users\Lenovo\Desktop\automation\version\S-gNB6810\test.tar.gz'
    # filepath = r'C:\Users\Lenovo\Desktop\automation\version\S-gNB6810_V921R001C010SPC100B040.20250124164310.tar.gz'
    # uncompress_tar_gz_file(filepath)
    filepath = r'C:\Users\Lenovo\Desktop\tsx_auto\version\D2000V_20250501002107'
    nr_cfg_Data = find_config_file(filepath, 'nr_cfg_Data.xml')
    modify_xml_file(nr_cfg_Data, obtain_cfg_json("modify_net_cfg_Data.json"))
    nr_cfg_Data = find_config_file(filepath, 'data.xml')
    modify_xml_file(nr_cfg_Data, obtain_cfg_json("modify_net_cfg_Data.json"))
    # find_xml_file_text(nr_cfg_Data,".//NR_POWER_OFFSET/dlAD")
    # find_xml_file_text(nr_cfg_Data,".//NR_POWER_OFFSET/ulAD")
    scf_gNbCfg = find_config_file(filepath, 'scf_gNbCfg.json')
    modify_json_file(scf_gNbCfg, obtain_cfg_json('modify_scf_gNbCfg.json'))
    # filepath = r'C:\Users\Lenovo\Desktop\automation\version\nrue_cfg_Data.xml'
    # find_xml_file_text(filepath,".//NR_TRACE_SERVER/serverIp")
    # modify_xml_file(filepath,obtain_cfg_json("modify_nrue_cfg_Data.json"))
    # filepath = uncompress_tar_gz_file(r'C:\Users\Lenovo\Desktop\automation\version\ue_starcom_prototype_version
    # .20250124120949.tar.gz')
    # nrue_cfg_Data = find_config_file(filepath,'nrue_cfg_Data.xml')
    # modify_xml_file(nrue_cfg_Data,obtain_cfg_json("modify_nrue_cfg_Data.json"))
    # organize_compress_sgnb_documents(filepath)
    # ue_filepath = r'C:\Users\Lenovo\Desktop\automation\version\ue_starcom_prototype_version.20250124120949'
    # organize_compress_ue_documents(ue_filepath,'stack')
    # organize_compress_ue_documents(ue_filepath,'phy')
    # get_deepest_keys(obtain_cfg_json("modify_scf_gNbCfg.json"))
    pass
