import re
import asyncio
import telnetlib3
import common.readBasicConfig as rbc

class VamClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.reader = None
        self.writer = None

    async def connect(self):
        """异步连接设备"""
        try:
            self.reader, self.writer = await telnetlib3.open_connection(
                host=self.ip, port=self.port, connect_maxwait=5
            )
            print(f"VAM telnet connect success! IP: {self.ip}, Port: {self.port}")
        except Exception as e:
            raise ConnectionError(f"Telnet login failed, IP: {self.ip}, Port: {self.port}, Error: {e}")

    async def send(self, cmd, output_print=True):
        """发送命令并获取输出"""
        if not self.writer:
            raise RuntimeError("Telnet connection is not established.")

        print(f"Sending Telnet command: '{cmd}'")
        self.writer.write(f"{cmd}\r\n")

        try:
            output = await self.reader.readuntil(b";\r\n")
            output = output.decode("utf-8", "ignore")
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout while waiting for response to command: {cmd}")

        # 处理心跳消息，仅获取命令回显
        pattern = re.compile(r">>.*;\r\n")
        valid_output = pattern.findall(output)

        if "fail" in output.lower():
            raise RuntimeError(f"Telnet command '{cmd}' failed with response: {output}")
        elif not valid_output:
            raise RuntimeError(f"No valid response for command: {cmd}")
        elif len(valid_output) > 1:
            raise RuntimeError(f"Abnormal response for command: {cmd}. Check if software is used elsewhere.")

        if output_print:
            print(valid_output[0])
        return valid_output[0]

    async def close(self):
        """关闭 Telnet 连接"""
        if self.writer:
            self.writer.close()
            print("Telnet connection closed.")

async def get_telnet_output(ip, port, cmd, output_print=True):
    """获取 Telnet 命令输出"""
    client = VamClient(ip, port)
    try:
        await client.connect()
        output = await client.send(cmd, output_print)
        return output
    finally:
        await client.close()

def send_cmd(ip, port, cmd, output_print=True):
    """发送命令并处理异常"""
    try:
        output = asyncio.run(get_telnet_output(ip, port, cmd, output_print))
        return output
    except Exception as e:
        raise RuntimeError(f"VAM telnet command '{cmd}' failed: {e}")

def set_attenuation(ip, port, num, value):
    """设置衰减值"""
    cmd = f"SA{num} {value}"
    send_cmd(ip, port, cmd)

def block_all_channels(ip,port):
    """阻塞所有通道"""
    for i in range(1, 5):
        cmd = f"SA{i} 110"
        send_cmd(ip, port, cmd)

if __name__ == "__main__":
    # 示例用法
    IP = rbc.get_vam_cfg()["vam_ip"]
    PORT = rbc.get_vam_cfg()["vam_port"]
    try:
        # set_attenuation(IP, PORT, 2, 20)
        block_all_channels(IP, PORT)
    except Exception as e:
        print(f"Error: {e}")