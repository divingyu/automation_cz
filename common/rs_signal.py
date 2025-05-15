from RsInstrument.RsInstrument import RsInstrument
from conf.testData import TsxData


class Signal:
    def __init__(self, signal_ip: str):
        try:
            self.resource_string = f"TCPIP::{signal_ip}::hislip0::INSTR"
            self.instr = RsInstrument(self.resource_string, True, False)
        except Exception:
            try:
                print("连接信号源失败, 重新连接")
                self.resource_string = f"TCPIP::{signal_ip}::hislip0::INSTR"
                self.instr = RsInstrument(self.resource_string, True, False)
            except Exception as e:
                print(f"连接信号源失败, 请检查信号源IP地址是否正确, 错误信息: {e}")
                raise e

    def arb_waveform_cfg(
            self,
            arb_waveform_path: str,
            center_freq: str = TsxData.SINGAL_MID_FREQ.value,
            samples_ta: str = TsxData.SINGAL_TA.value,
            clock_freq: str = TsxData.SINGAL_CLOCK_FREQ.value,
    ):
        self.instr.write_str(f":SOUR1:FREQ {center_freq}")
        self.instr.write_str(f':SOUR1:BB:ARB:WAV:SEL "{arb_waveform_path}"')
        # self.instr.write_str(f':SOURce1:BB:ARBitrary:WAVeform:SELect "{arb_waveform_path}"')
        self.instr.write_str(f":SOUR1:BB:ARB:CLOCK {clock_freq}")
        # 设置触发模式为Single
        self.instr.write_str(":SOURce1:BB:ARBitrary:TRIGger:SEQuence SING")
        # 设置为外部触发1
        self.instr.write_str(":SOURce1:BB:ARBitrary:TRIGger:SOURce EGT1")
        # 设置外部时延为200 samples
        self.instr.write_str(
                f":SOURce1:BB:ARBitrary:TRIGger:EXTernal1:DELay {samples_ta}"
        )
        # 打开ARB开关
        self.instr.write_str(":SOUR1:BB:ARB:STAT ON")

    def awgn_cfg(
            self,
            snrpwr: str,
            outputpwr: str,
            bwid: str = TsxData.SINGAL_AWGN_BWID.value,
            bitrate: str = TsxData.SINGAL_AWGN_BIT_RATE.value,
    ):
        self.instr.write_str(f":SOUR1:AWGN:BWID {bwid}")
        self.instr.write_str(f":SOURce1:AWGN:BRATe {bitrate}")
        self.instr.write_str(f":SOUR1:AWGN:SNR {snrpwr}dB")
        self.instr.write_str(f":SOUR1:POW {outputpwr}dBm")
        # 启用AWGN
        self.instr.write_str(":SOUR1:AWGN:STAT ON")

    def open_rf(self):
        ## 打开RF
        self.instr.write_str(":OUTP1:STAT ON")

    def close_rf(self):
        self.instr.write_str(":OUTP1:STAT OFF")
        self.instr.close()

    def close_connect(self):
        self.instr.close()

    def singal_decode_tmp(
            self,
            arb_waveform_path: str,
            snrpwr: str,
            outputpwr: str,
            center_freq: str = TsxData.SINGAL_MID_FREQ.value,
            samples_ta: str = TsxData.SINGAL_TA.value,
            clock_freq: str = TsxData.SINGAL_CLOCK_FREQ.value,
            bwid: str = TsxData.SINGAL_AWGN_BWID.value,
            bitrate: str = TsxData.SINGAL_AWGN_BIT_RATE.value,
    ):
        self.arb_waveform_cfg(arb_waveform_path, center_freq, samples_ta, clock_freq)
        self.awgn_cfg(snrpwr, outputpwr, bwid, bitrate)
        self.open_rf()
        self.close_connect()

    def singal_pujc_tmp(self, center_freq: str, outputpwr: str = "-20"):
        self.instr.write_str("*RST")
        self.instr.write_str(f":SOUR1:FREQ {center_freq}")
        self.instr.write_str(f":SOUR1:POW {outputpwr}dBm")
        self.open_rf()

    def singal_obtain_freq(self) -> float:
        freq_with_unit = self.instr.query_str(":SOUR1:FREQ?")
        singal_freq = float(freq_with_unit.strip()) / 1e6
        return singal_freq

# if __name__ == "__main__":
#     print(TestData.D2000V_NEW_PATH.value)