"""
Company            :
Create Date        : 2025-01-24 14:05:05
Engineer           : You Yuling
Target Devices     : ftp
Tool Versions      : v_1.0
Description        : obtain sgnb and ue the newest version
Revision           : LastEditTime
"""
import os
import re
import ftplib
from tqdm import tqdm
import common.readBasicConfig as rbc


class FtpServ:
    def __init__(self, cfg_data: dict):
        self.ftp_ip = cfg_data['ftp_ip']
        self.ftp_user = cfg_data['ftp_user']
        self.ftp_password = cfg_data['ftp_pwd']
        self.FTP_VENUS_DAILY_VER_PATH = cfg_data['FTP_VENUS_DAILY_VER_PATH']
        self.FTP_PROTOTYPE_DAILY_VER_PATH = cfg_data['FTP_PROTOTYPE_DAILY_VER_PATH']
        self.ftp = ftplib.FTP(self.ftp_ip)
        self.ftp.login(self.ftp_user, self.ftp_password)

    def obtain_venus_newest_version(self) -> str:
        newest_version = self.ftp.nlst(self.FTP_VENUS_DAILY_VER_PATH)[-1]
        file_newest_version = self.ftp.nlst(newest_version)[1]
        print(file_newest_version)
        return file_newest_version

    def obtain_venus_file(self, filename: str) -> str:
        try:
            filename = os.path.basename(filename)
            file_fold = re.search(r'\.?(\d{12,})', filename).group(1)
            venus_ver_list = self.ftp.nlst(self.FTP_VENUS_DAILY_VER_PATH)
            for venus_ver in venus_ver_list:
                if file_fold in venus_ver:
                    return self.ftp.nlst(venus_ver)[-1]
            raise AttributeError(f"{filename} is not exist!!")
        except AttributeError:
            raise AttributeError(f"{filename} is not exist!!")

    def obtain_prototype_newest_version(self) -> str:
        newest_version = self.ftp.nlst(self.FTP_PROTOTYPE_DAILY_VER_PATH)[-1]
        file_newest_version = self.ftp.nlst(newest_version)[-1]
        return file_newest_version

    def obtain_prototype_file(self, filename: str) -> str:
        try:
            filename = os.path.basename(filename)
            file_fold = re.search(r'\.?(\d{12,})', filename).group(1)
            prototype_ver_list = self.ftp.nlst(self.FTP_PROTOTYPE_DAILY_VER_PATH)
            for prototype_ver in prototype_ver_list:
                if file_fold in prototype_ver:
                    return self.ftp.nlst(prototype_ver)[-1]
            raise AttributeError(f"{filename} is not exist!!")
        except AttributeError:
            raise AttributeError(f"{filename} is not exist!!")

    def file_is_exist(self, filepath: str) -> bool:
        file_list = self.ftp.nlst(filepath)
        if len(file_list) == 0:
            return False
        file_list = self.ftp.nlst(f"{filepath}/")
        if len(file_list) == 0:
            return True
        return False

    def download_version_files(self, *remote_file_paths) -> list:
        try:
            local_file_paths = []
            for i, remote_file_path in enumerate(remote_file_paths):
                if not self.file_is_exist(remote_file_path):
                    raise AttributeError(f"{remote_file_path} is not exist!!")
                filename = os.path.basename(remote_file_path)
                local_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'version'))
                if not os.path.exists(local_file_path):
                    os.mkdir(local_file_path)
                local_filename = os.path.join(local_file_path, filename)
                file_size = self.ftp.size(remote_file_path)
                with open(local_filename, 'wb') as local_file:
                    with tqdm(total=file_size, unit='B', unit_scale=True, desc=remote_file_path, ncols=None, ascii=True,
                              position=i) as pbar:
                        def callback(data):
                            local_file.write(data)
                            pbar.update(len(data))

                        self.ftp.retrbinary(f"RETR {remote_file_path}", callback)
                local_file_paths.append(local_filename)
            return local_file_paths
        except ftplib.error_perm as e:
            print(f"F Error: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")


if __name__ == '__main__':
    ftp = FtpServ(rbc.get_ftp_cfg())
    ftp.download_version_files(rbc.LOCAL_LOG_PATH,
                               ftp.obtain_prototype_newest_version(),
                               ftp.obtain_venus_newest_version())
