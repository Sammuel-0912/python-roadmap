# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

本專案在 **Windows 11**、Python **3.13**、使用 `uv` 建立的 **`.venv`** 虛擬環境下開發。

## 架構：三階段資料流水線

三個腳本以 CSV 檔案為介面串接，**沒有直接互相 import**，靠中間產物傳遞資料。順序很重要，後段依賴前段的輸出：

1. **`main.py`** — FastAPI 爬蟲服務。非同步（`httpx` + `asyncio.gather`）爬 `quotes.toscrape.com`，用 BeautifulSoup 解析，經 Pandas 清洗後寫出 `quotes.json_cleaned.csv`。
   - `fetch_page()` 抓網頁、`parse_quotes()` 解析 HTML，兩者是純函式、可單獨測試。
   - 路由：`GET /api/quotes`（回傳 JSON）、`GET /api/save_csv`（清洗並存 CSV）。都用 `start_page` / `end_page` 查詢參數。
   - CSV 存檔用 `encoding="utf-8-sig"`，確保 Excel 開啟不亂碼；tags 串列會被壓成 `" , "` 分隔字串。
2. **`analyze.py`** — 讀 `quotes.json_cleaned.csv`，用 seaborn/matplotlib 產生 `top_authors.png`，用 wordcloud 產生 `tag_wordcloud.png`。純繪圖存檔，不開視窗。
3. **`ai_analysis.py`** — 讀 `quotes.json_cleaned.csv`，用 Hugging Face `transformers` pipeline（DistilBERT SST-2）做情感分析，加上 `ai_sentiment` / `ai_score` 欄位後寫出 `quotes_with_ai.csv`。首次執行會自動下載約 268MB 模型並快取。

**改動注意**：若改了 `main.py` 清洗邏輯的欄位名（如 `quote`、`author`、`tags`），`analyze.py` 與 `ai_analysis.py` 會跟著壞，因為它們靠欄位名讀資料。

## 執行方式

一律用 venv 的 Python 執行（`uv` 建立的 `.venv`）：
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt   # 安裝依賴
.\.venv\Scripts\python.exe main.py          # 啟動 API，http://127.0.0.1:8000（reload 開啟）
.\.venv\Scripts\python.exe analyze.py       # 由 cleaned CSV 產生圖表
.\.venv\Scripts\python.exe ai_analysis.py   # 情感分析，產生 quotes_with_ai.csv
```
- 目前**沒有**自動化測試。若要新增，放在 `tests/`、命名 `test_*.py`，優先測純函式（`parse_quotes()`、`load_data()`、DataFrame 轉換）。
- 沒有 build 步驟；煙霧測試就是跑對應腳本、確認輸出檔有更新。

## 環境常見錯誤與對策（Windows + uv venv 踩過的坑）

### 1. `Can't find a usable init.tcl` / Tcl 找不到（tkinter、matplotlib）
- **原因**：`uv` 建立的 `.venv` 在 Windows 上不會設定 Tcl/Tk 路徑，matplotlib 預設 `tkagg` 後端因此找不到 Tcl。系統 Python 本身正常，**Tcl 沒有壞**。
- **只存圖、不開視窗的腳本**：在 `import matplotlib.pyplot` 之前加：
  ```python
  import matplotlib
  matplotlib.use("Agg")   # 不需 GUI，完全繞開 Tcl/Tk
  import matplotlib.pyplot as plt
  ```
- **真的需要 GUI（tkinter 視窗、plt.show() 互動顯示）**：設環境變數指向系統 Python 的 Tcl：
  ```powershell
  $env:TCL_LIBRARY = "C:\Users\sam60\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"
  $env:TK_LIBRARY  = "C:\Users\sam60\AppData\Local\Programs\Python\Python313\tcl\tk8.6"
  ```

### 2. `UnicodeEncodeError: 'cp950' codec can't encode ...`（印 emoji / 中文報錯）
- **原因**：Windows 終端機預設用 cp950（Big5），印不出 emoji。
- **對策**：腳本開頭加：
  ```python
  import sys
  sys.stdout.reconfigure(encoding="utf-8")
  ```

## matplotlib / wordcloud 慣用寫法
- `WordCloud` 的 `background_color` 要放**顏色**（如 `"white"`），色譜（`"plasma"`、`"viridis"`）要放 `colormap=`，不要搞混。
- 合併標籤字串用空格分隔：`" ".join(tags)`，不要用 `"".join(tags)`（會黏成一個字）。

## 慣例
- 4 空格縮排；函式與變數 `snake_case`，類別 `PascalCase`。
- 檔案存 UTF-8；輸出檔用描述性名稱（`quotes_with_ai.csv`、`top_authors.png`）。
- 產生的 CSV / PNG 寫在 repo 根目錄；除非刻意要納入版控，否則不要 commit 重新產生的大型輸出。
