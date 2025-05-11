from enum import Enum, unique

# @unique
class TsxData(Enum):
    # D2000V_PUJC_PATH = r"C:\Users\Lenovo\Desktop\tsx_auto\version\Ver_20250412_0800\zhengyang\S-gNB6810_V021R001C010SPC100B040_debug.20250412002130\D2000V"
    D2000V_PUJC_PATH = r"C:\Users\Lenovo\Desktop\tsx_auto\version\D2000V_20250501002107"
    GTESTPHY_F1_RX0_MCS0_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_F1_RX0_MCS0"
    GTESTPHY_F1_RX0_MCS25_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_F1_RX0_MCS25"
    GTESTPHY_F1_RX1_MCS0_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_F1_RX1_MCS0"
    GTESTPHY_F1_RX1_MCS25_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_F1_RX1_MCS25"
    GTESTPHT_F1_TX_EVM_MCS0_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_F1_TX_EVM_MCS0"
    GTESTPHT_F1_TX_EVM_MCS16_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_F1_TX_EVM_MCS16"
    GTESTPHT_F1_TX_SUB_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_F1_TX_sub"
    GTESTPHY_RX0_PUCCH_F1_FM0 = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_PUCCH_F1_200M_FM0_RX0"
    GTESTPHY_RX1_PUCCH_F1_FM0 = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_PUCCH_F1_400M_FM0_RX1"
    GTESTPHT_F2_RX0_MCS0_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_F2_RX0_MCS0"
    GTESTPHT_F2_RX0_MCS25_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_F2_RX0_MCS25"
    GTESTPHT_F2_RX1_MCS0_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_F2_RX1_MCS0"
    GTESTPHT_F2_RX1_MCS25_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_F2_RX1_MCS25"
    GTESTPHT_F2_TX_EVM_MCS0_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_F2_TX_EVM_MCS0"
    GTESTPHT_F2_TX_EVM_MCS16_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_F2_TX_EVM_MCS16"
    GTESTPHT_F2_TX_SUB_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_F2_TX_sub"
    GTESTPHY_RX0_PUCCH_F2_FM0 = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_PUCCH_F2_200M_FM0_RX0"
    GTESTPHY_RX1_PUCCH_F2_FM0 = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_PUCCH_F2_200M_FM0_RX1"
    GTESTPHT_F1_TX_PRACH_FM10_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_PRACH_F1_FM10"
    GTESTPHT_F1_TX_PRACH_FM4_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_PRACH_F1_FM4"
    GTESTPHT_F2_TX_PRACH_FM10_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_PRACH_F2_FM10"
    GTESTPHT_F2_TX_PRACH_FM4_PATH = r"C:\Users\Lenovo\Desktop\shijiazhuang\gtestphy\gTestPhy_PRACH_F2_FM4"
    TSHARK_PATH = "D:\\Application\\RelWithDebInfo\\"
###############################################################
### 信号源参数设置
    SINGAL_MID_FREQ = "2.25GHZ"
    # SINGAL_MID_FREQ = "2.250017859GHZ"
    # SINGAL_MID_FREQ = "2.24998812GHZ"
    SINGAL_TA = "2500"
    SINGAL_CLOCK_FREQ = "491.52MHz"
### 配置白噪声
    SINGAL_AWGN_BWID = "491.52MHz"
    SINGAL_AWGN_BIT_RATE = "336128000"
