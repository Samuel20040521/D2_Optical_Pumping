# D2 Optical Pumping — 銣原子光學幫浦資料分析

近代物理實驗 D2「銣原子光學幫浦」的完整資料分析倉庫。我們在同一個鈉銣蒸氣管上做四個串接的子實驗——共振吸收、低場 Zeeman、二次 Zeeman (Breit–Rabi) 與暫態幫浦動力學——並把整條校正鏈與不確定度傳遞做到自洽。

主要結果（細節詳見 [reports/main.pdf](reports/main.pdf)）：

- **4a 共振吸收**：由三段熱循環的 Beer–Lambert 擬合得到有效吸收截面 $\sigma_{\mathrm{exp}} = 1.766(50)\times 10^{-16}\ \mathrm{m^2}$。
- **4b 低場 Zeeman**：斜率比 $m_{87}/m_{85} = 1.554(22)$ 確定核自旋 $I_{87}=3/2$、$I_{85}=5/2$；sweep coil 校正常數 $k_{\mathrm{sweep}} = 0.6397(39)\ \mathrm{G/A}$，殘餘地磁 $|B_0| = 0.2263(24)\ \mathrm{G}$；延伸到 200 kHz–1 MHz 得 main coil 校正常數 $k_{\mathrm{main}} = 8.579(24)\ \mathrm{G/A}$。
- **4c 二次 Zeeman**：在 $B \simeq 7\ \mathrm{G}$ 解析出 Breit–Rabi fan，$^{87}\mathrm{Rb}$ 五條、$^{85}\mathrm{Rb}$ 全十條躍遷與數值解一致到 0.1%。
- **4d 暫態動力學**：幫浦時間常數比 $\tau_p^{87}/\tau_p^{85} = 1.20005(22)$，與 Franzen–Emslie 速率方程模擬 (1.164) 在 3% 內吻合，Rabi 振盪頻率 $f_R = 3035.062(80)\ \mathrm{Hz}$ 並符合 $T \propto 1/V_{\mathrm{rf}}$。

---

## 資料夾分工

```text
.
├── data/raw/               # 從 Google Drive 下載的原始示波器資料
├── notebook/               # Jupyter Notebook：所有資料處理細節都在這
│   ├── 4a.ipynb            #   共振吸收 (Beer–Lambert)
│   ├── 4b_pre.ipynb        #   4b/4c 共用的 cycle 切割 + dip 偵測 pipeline
│   ├── 4b.ipynb            #   低場 Zeeman 與磁場校正
│   ├── 4c.ipynb            #   Breit–Rabi 二次 Zeeman
│   ├── 4d.ipynb            #   暫態：optical pumping τ_p 與 Rabi ringing
│   └── Optical_Pumping_Rate_Equation_Model.ipynb  # Franzen–Emslie 數值模擬
├── src/                    # 可重用的分析模組（被 notebook 匯入）
│   ├── analysis/           #   含誤差傳遞的線性／非線性回歸與格式化
│   ├── signal/             #   週期切割 (segmentation) 與 dip detection
│   ├── logic/              #   dip → quantum number tag 的分類邏輯
│   ├── uncertainty/        #   A 類 + B 類組合不確定度
│   ├── utils/              #   檔名／metadata 解析
│   └── visualization/      #   黑白列印友善的圖風格與 figure helpers
├── reports/                # LaTeX 報告原始檔
│   ├── main.tex            #   主文件（編譯後輸出 main.pdf）
│   ├── main.pdf            #   完整報告
│   ├── section/            #   各章節 .tex（abstract / 4a / 4b / 4c / 4d / Q&A / Appendix）
│   ├── Apparatus/, Theory/ #   附錄性質的儀器與理論說明
│   ├── reference.bib       #   參考文獻
│   ├── theory pics/        #   理論章節用圖
│   └── figures/            #   notebook 輸出的 PDF/PNG 圖檔（被 main.tex 引用）
├── docs/                   # 參考資料（lab manual 影像與 markdown）
│   ├── Berkeley/           #   Berkeley OP 講義
│   └── OP1-B/              #   TeachSpin OP1-B 手冊
├── pyproject.toml          # uv 管理的依賴
├── .python-version         # 鎖定 Python 版本
└── uv.lock
```

每個資料夾的職責：

- **`notebook/`**：你執行分析的入口。每一本 notebook 對應報告中的一個小節，並把所有探索性的處理流程（讀檔、切 cycle、找 dip、擬合、畫圖、輸出）寫在 cell 裡。
- **`src/`**：當 notebook 裡的某段邏輯穩定下來、會被多本 notebook 重用時，就搬到 `src/`。例如 `src/signal/segmentation.py` 把示波器 trace 依 sweep 週期切段，`src/logic/tagger.py` 把找到的 dip 對到 $(F, m_F)$ 量子數。
- **`data/raw/`**：原始示波器與量測檔案，**只讀**。請用下面 §3 的指令從 Google Drive 下載。
- **`reports/figures/`**：notebook 跑完會自動把圖輸出到這裡，並被 `reports/main.tex` 直接引用。
- **`reports/`**（除了 `figures/`）：寫好的 LaTeX 報告。`main.tex` 會 `\input` `section/*.tex`，這些章節是把 notebook 的數值結果加上物理討論後的最終文字版本。
- **`docs/`**：lab manual 與背景參考。Berkeley 與 TeachSpin OP1-B 兩套手冊原文（已轉成 markdown + 抽出的圖），用來查公式與儀器規格。

---

## 從零跑通：環境 → 資料 → Notebook

### 1. 安裝 `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# 重開 shell 後驗證
uv --version
```

### 2. 建立虛擬環境並安裝依賴

在專案根目錄執行：

```bash
uv sync --group dev
```

這會根據 `pyproject.toml` 與 `uv.lock` 在 `.venv/` 建出環境，並安裝 `numpy`、`scipy`、`pandas`、`matplotlib`、`uncertainties`、`sympy`、Jupyter、`ipykernel` 等。

### 3. 註冊 Jupyter kernel（使用 `.venv`）

```bash
uv run python -m ipykernel install --user \
  --name d2-optical-pumping \
  --display-name "Python (.venv) D2"
```

之後在 VS Code 或 Jupyter 介面打開 notebook 時，把 kernel 切到 **Python (.venv) D2** 即可。

### 4. 下載原始資料到 `data/raw/`

原始檔放在 Google Drive，用 `gdown` 拉下來：

```bash
uv tool install gdown   # 若尚未安裝
gdown --folder "https://drive.google.com/drive/folders/1oSah8gFO4-Oxz7PDxcv1roB1UgOJDfUz?usp=drive_link" \
      -O data/raw/
```

下載完成後 `data/raw/D2_Optical_Pumping/` 底下會有四個量測日的子資料夾：

| 子資料夾 | 內容 | 對應 notebook |
| --- | --- | --- |
| `0323/` | Beer–Lambert 三段熱循環的電壓 vs 溫度 (`run{1,2,3}_*.dat`) + Killian 密度表 | `4a.ipynb` |
| `0330/` | 低場 Zeeman dip 掃描 (`85_Q.csv`、`87_Q.csv`、`B0.csv`) | `4b.ipynb` |
| `0402/` | RF 振幅掃描 (`{85,87}_{1,2,3}Vpp.csv`) | `4d.ipynb` |
| `0413/` | 高頻磁場校正與 Breit–Rabi (`*KHZ_*.csv`、`{85,87}_Q.ZEEMAN.csv`) | `4b.ipynb`、`4c.ipynb` |

### 5. 執行分析

啟動 Jupyter：

```bash
uv run jupyter lab
```

建議的執行順序（與報告章節對應）：

1. **`4a.ipynb`** — 共振吸收、Beer–Lambert 擬合、$\sigma_{\mathrm{exp}}$。
2. **`4b_pre.ipynb`** — 4b/4c 共用的 pipeline：把示波器 trace 依 sweep 切 cycle、找出 dip、依 quantum number 標記。產生中介資料供 4b、4c 使用。
3. **`4b.ipynb`** — 低場 Zeeman、核自旋判定、sweep / main coil 校正。
4. **`4c.ipynb`** — Breit–Rabi 數值解、與量測 dip 比對。
5. **`4d.ipynb`** — 幫浦時間常數 $\tau_p$ 擬合、CH2 ringing 的阻尼正弦擬合、$f_R(V_{\mathrm{rf}})$ 線性回歸。
6. **`Optical_Pumping_Rate_Equation_Model.ipynb`** — 由 Clebsch–Gordan 係數出發的多能階速率方程，作為 4d 觀察到 $\tau_p^{87} > \tau_p^{85}$ 的理論交叉檢查。

每本 notebook 跑完會把對應的 PDF 圖輸出到 `reports/figures/`，這些檔名會直接對應到 `reports/main.tex` 的 `\includegraphics` 引用。

### 6. 編譯報告（可選）

報告以 XeLaTeX + biber 編譯（因為使用 `xeCJK`）：

```bash
cd reports
latexmk -xelatex -bibtex main.tex
```

或直接看已編好的 [reports/main.pdf](reports/main.pdf)。

---

## 常用指令

```bash
uv sync --group dev                    # 安裝 / 同步依賴
uv run jupyter lab                     # 啟動 notebook
uv run pytest                          # 執行測試
uv run python path/to/script.py        # 執行單一腳本
uv add <package>                       # 新增依賴
```

---

## `src/` 內的可重用模組

| 模組 | 用途 |
| --- | --- |
| `src.uncertainty.get_combined_ufloat(data, resolution)` | 從重複量測值組合 A 類 + B 類不確定度，回傳 `ufloat`。 |
| `src.analysis.fitting.excel_style_regression_with_propagation` | 線性回歸並把 $x$、$y$ 不確定度傳遞到斜率／截距。 |
| `src.analysis.fitting.nonlinear_regression_with_propagation` | 一般非線性模型擬合，回傳含不確定度的參數與協方差。 |
| `src.analysis.formatting.ufloat_to_paren` | 把 `ufloat` 格式化成物理慣用的括號表示（如 `1.34836(43)`）。 |
| `src.signal.segmentation.extract_valid_cycles` | 把示波器 trace 依 sweep 訊號切成單一 sweep 週期。 |
| `src.signal.detection.detect_dips` | 從切好的 cycle 中找 Zeeman 吸收 dip。 |
| `src.logic.tagger.assign_tags` | 把找到的 dip 對到 $(F, m_F \to m_F')$ quantum number。 |
| `src.utils.file_parser.parse_metadata` | 從檔名解析量測條件（同位素、頻率、Vpp 等）。 |
| `src.visualization.plot_settings` | 統一的 matplotlib 風格（serif、STIX、黑白列印友善），以及 `create_figure` / `save_figure` helper。 |

---

## 備註

- `data/raw/`、`reports/figures/` 內容大多由 notebook 或下載產生。`main.pdf`、報告原始碼與 `reports/figures/` 會被版本控制，原始資料則靠 `gdown` 重建。
- LaTeX 編譯產物（`*.aux`、`*.log`、`*.bbl` 等）已在 `.gitignore` 排除。
- 若要驗證安裝，最快的健全測試是直接跑 `4a.ipynb`：它只用到 `0323/` 的小檔案，幾秒內就能跑完並產生 `4a_T_I_plot.pdf` 與 `4a_Combined_Fit_Hysteresis.pdf`。
