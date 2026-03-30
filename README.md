# Modern Physics Experiment Data Analysis Template

這個 repository 是給近代物理實驗或一般實驗課使用的資料分析模板。它把 `D1_temp` 中較通用、可重複使用的部分整理成一個乾淨的 GitHub template，目標是讓每次開新實驗專案時，都能直接沿用一致的資料夾結構、分析模組與 Python 環境。

專案重點：

- 保留原始資料與處理後資料的分層，方便追溯
- 用 `src/` 集中放可重用的分析與繪圖程式
- 用 `uv` 管理 Python 版本、虛擬環境與依賴
- 預先放入常用的 `fitting.py` 與 `formatting.py`

## 資料夾結構

```text
.
├── .github/
│   └── copilot-instructions.md
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── metadata/
├── docs/
├── notebook/
├── reports/
│   ├── figures/
│   └── tables/
├── src/
│   ├── analysis/
│   │   ├── fitting.py
│   │   └── formatting.py
│   ├── io/
│   ├── preprocessing/
│   ├── uncertainty/
│   └── visualization/
├── tests/
├── .gitignore
├── .python-version
└── pyproject.toml
```

## 每個資料夾的用途

### `.github/`

放 GitHub 相關設定。這裡目前提供 `copilot-instructions.md`，讓 AI 工具或協作者更容易理解這個專案的分析流程與資料管理原則。

### `data/raw/`

放原始實驗資料。建議把這裡當成只讀區，不要直接修改檔案內容。像是儀器匯出的 `.csv`、`.txt`、手抄後建成的原始表格，都應該先放在這裡。

### `data/interim/`

放中間清理結果，例如：

- 改過欄位名稱的資料
- 合併後但還沒正式定稿的表格
- 暫時做過單位轉換或格式整理的資料

### `data/processed/`

放最終可直接分析或畫圖的資料。這些檔案通常已經完成：

- 單位統一
- 校正
- 誤差欄位補齊
- 分析前的欄位整理

### `data/metadata/`

放輔助說明資料，例如：

- 欄位定義
- 實驗條件說明
- 儀器解析度與校正常數
- 樣本或批次對照表

### `docs/`

放方法說明、分析筆記、實驗流程整理、期末報告草稿等文字文件。當某段分析邏輯太長，不適合只寫在 notebook 註解裡時，可以移到這裡。

### `notebook/`

放 Jupyter Notebook。適合做：

- 初步資料探索
- 嘗試擬合流程
- 圖表樣式微調
- 課堂展示

當 notebook 裡的程式變穩定後，建議把核心邏輯搬到 `src/`。

### `reports/figures/`

放輸出的圖檔，例如 PDF、PNG、SVG。通常是要貼進報告或簡報的圖。

### `reports/tables/`

放整理好的表格輸出，例如：

- CSV
- LaTeX table
- Markdown table

### `src/analysis/`

放數值分析、擬合、回歸、物理量推導等核心函式。

目前內含：

- `fitting.py`：提供帶有誤差傳播概念的線性回歸函式
- `formatting.py`：把 `uncertainties.ufloat` 格式化成物理報告常用的括號表示法

### `src/io/`

放讀寫資料的函式，例如讀取 CSV、Excel、TXT、儀器輸出格式等。

### `src/preprocessing/`

放資料清理、重塑、合併、欄位整理、單位轉換等前處理邏輯。

### `src/uncertainty/`

放不確定度分析工具，例如：

- Type A / Type B 不確定度
- 誤差傳遞
- Monte Carlo propagation
- 不確定度預算表

### `src/visualization/`

放繪圖邏輯與全域作圖設定。建議將可重用的圖表樣式與繪圖函式集中在這裡，而不是散落在 notebook。

模板已經提供統一的作圖接口與 style preset，放在 `src/visualization/plot_settings.py`。你之後如果想沿用 `D1_temp` 的畫圖風格，通常只需要改：

- `xlabel`
- `ylabel`
- `figsize`

其他像字體、數學字型、刻度方向、格線、輸出 DPI、圖例風格、輸出路徑等，都可以保持一致。

### `tests/`

放自動化測試。即使只是簡單模板，也建議至少替重要公式或格式化函式加上基本測試，避免之後改壞。

## 內建工具模組

### `src/analysis/fitting.py`

提供 `excel_style_regression_with_propagation()`，可做線性回歸並把 `x`、`y` 的不確定度傳遞到斜率與截距。這類功能很適合聲速、衰減、校正常數等線性模型分析。

### `src/analysis/formatting.py`

提供 `ufloat_to_paren()`，可把 `uncertainties.ufloat` 轉成物理報告慣用格式，例如：

```python
from uncertainties import ufloat
from src.analysis.formatting import ufloat_to_paren

value = ufloat(1.34836, 0.00043)
print(ufloat_to_paren(value))
# 1.34836(43)
```

## 內建作圖接口

`D1_temp/src/visualization/` 的共通格式，已經整理成 template 可直接重用的接口：

- serif 字體搭配 STIX 數學字型
- 預設圖大小 `6.5 x 4.5`
- `savefig.dpi = 300`
- inward ticks 與 minor ticks
- 淡色虛線 grid
- 預設不顯示上、右邊框
- 預設無外框 legend

如果你要畫一般分析圖：

```python
import numpy as np

from src.visualization import create_figure, save_figure

x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = create_figure(
    xlabel="Distance [mm]",
    ylabel="Signal [a.u.]",
    figsize=(6.5, 4.5),
)

ax.plot(x, y, label="data")
ax.legend()

save_figure(fig, "example_plot.pdf")
```

如果你要先套用比較圖或寬圖 preset，再自己手動建立多子圖版面：

```python
import matplotlib.pyplot as plt

from src.visualization import apply_plot_style

apply_plot_style("comparison")
fig, axes = plt.subplots(1, 2, figsize=(10, 13), constrained_layout=True)
```

目前提供三種 preset：

- `base`：一般單張分析圖，對應 `D1_temp` 的主流格式
- `comparison`：大型比較圖，對應雙欄或點位標註很多的圖
- `wide`：超寬橫式比較圖，對應 `PHY11` 那種長條型展示

## 用 `uv` 建立環境

### 1. 安裝 `uv`

如果你的系統還沒有 `uv`，先安裝它：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安裝完成後重新打開終端機，確認版本：

```bash
uv --version
```

### 2. 建立專案環境

進入專案根目錄後執行：

```bash
uv sync --group dev
```

這個指令會：

- 建立 `.venv/`
- 安裝 `pyproject.toml` 中的依賴
- 安裝 notebook、pytest、ruff 等開發工具

### 3. 常用指令

執行 notebook：

```bash
uv run jupyter lab
```

執行測試：

```bash
uv run pytest
```

執行 Python 腳本：

```bash
uv run python path/to/script.py
```

新增套件：

```bash
uv add seaborn
```

新增開發用套件：

```bash
uv add --group dev black
```

### 4. Python 版本

目前模板預設使用 Python 3.11，並寫在 `.python-version`。如果你的系統已安裝 `uv`，通常可以直接讓 `uv` 幫你處理對應環境。

## 建議工作流程

1. 把原始資料放到 `data/raw/`
2. 在 `notebook/` 或 `src/preprocessing/` 先做整理
3. 中間產物放到 `data/interim/`
4. 最終可分析資料放到 `data/processed/`
5. 在 `src/analysis/` 做擬合、誤差分析與物理量計算
6. 在 `src/visualization/` 產生圖表
7. 把輸出圖表與表格放到 `reports/`

## 如何把這個 repo 當成 GitHub Template

這個資料夾內容已經整理成適合做 template 的形式。若你要在 GitHub 上正式啟用 Template Repository，還需要在 GitHub 網站上做一次設定：

1. 先把這個 repo push 到 GitHub
2. 進入該 repository 的 `Settings`
3. 勾選 `Template repository`
4. 之後就可以用 `Use this template` 建立新實驗專案

## 備註

- `reports/figures/`、`reports/tables/`、`data/interim/`、`data/processed/` 預設在 `.gitignore` 中忽略實際輸出，但保留 `.gitkeep` 以維持結構
- 如果某次實驗需要額外模組，例如頻譜分析、影像處理、非線性擬合，可以直接在 `src/` 下擴充
