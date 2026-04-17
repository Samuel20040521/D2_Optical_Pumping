import numpy as np
from uncertainties import ufloat


def get_combined_ufloat(data, resolution=None):
    """
    輸入一組實驗數據，自動計算 A 類、B 類與組合不確定度。

    參數:
    data (list or array): 測量數據列表。
    resolution (float, optional): 儀器的最小刻度。如果為 None，程式會嘗試自動偵測小數位數。

    回傳:
    ufloat: 包含平均值與組合不確定度的數值。
    """
    n = len(data)
    if n == 0:
        raise ValueError("數據列表不能為空！")

    # 1. 計算平均值
    mean_val = np.mean(data)

    # 2. 計算 A 類不確定度
    if n > 1:
        u_A = np.std(data, ddof=1) / np.sqrt(n)
    else:
        u_A = 0.0  # 如果只有一筆數據，A類不確定度為 0

    # 3. 處理 B 類不確定度的最小刻度
    if resolution is None:
        # 將數字轉成字串，找出小數點後最多的位數來推測刻度
        decimals = [len(str(x).split(".")[1]) for x in data if "." in str(x)]
        max_decimals = max(decimals) if decimals else 0
        resolution = 10 ** (-max_decimals)
        print(f"[系統提示] 未提供最小刻度，自動偵測為: {resolution}")

    u_B = resolution / np.sqrt(12)

    # 4. 組合不確定度
    u_c = np.sqrt(u_A**2 + u_B**2)

    return ufloat(mean_val, u_c)
