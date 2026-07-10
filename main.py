from pathlib import Path
import asyncio

import httpx
import pandas as pd
from bs4 import BeautifulSoup
from fastapi import FastAPI, Query

app = FastAPI(title="資料科學起步走", version="2.0")


async def fetch_page(client: httpx.AsyncClient, page_num: int) -> str:
    """負責發送非同步網路請求"""
    url = f"https://quotes.toscrape.com/page/{page_num}/"
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"錯誤 (頁數 {page_num}): {e}")
        return ""


async def scrape_quotes(start_page: int, end_page: int) -> list[dict]:
    """抓取指定頁數範圍內的名言資料。"""
    async with httpx.AsyncClient() as client:
        tasks = [fetch_page(client, page) for page in range(start_page, end_page + 1)]
        page_html = await asyncio.gather(*tasks)

    raw_data = []
    for html in page_html:
        raw_data.extend(parse_quotes(html))
    return raw_data


def parse_quotes(html_content: str) -> list[dict]:
    """負責解析 HTML 內容"""
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, "html.parser")
    quotes_data = []
    quote_elements = soup.find_all("div", class_="quote")

    for element in quote_elements:
        text = element.find("span", class_="text").text.strip()
        author = element.find("small", class_="author").text.strip()
        tags = [tag.text for tag in element.find_all("a", class_="tag")]
        quotes_data.append({"quote": text, "author": author, "tags": tags})
    return quotes_data


# --- 階段二：Pandas 整合路由 ---
@app.get("/api/save_csv")
async def save_quotes_to_csv(
    start_page: int = Query(1, ge=1), end_page: int = Query(5, ge=1)
):
    """
    爬取資料，並使用 Pandas 進行清洗後存成 CSV 檔
    """
    if end_page < start_page:
        return {"error": "結束頁數不能小於開始頁數"}

    # 1. 非同步爬取資料
    raw_data = await scrape_quotes(start_page, end_page)

    if not raw_data:
        return {"status": "失敗", "message": "為爬取到任何資料"}

    # 2. 將資料載入 Pandas DataFrame

    df = pd.DataFrame(raw_data)

    # 3. 資料清洗與特徵優化 (Data Cleaning & Feature Engineering)
    # 技巧 A: 新增一個欄位，計算每條名言有幾個標籤
    df["tag_count"] = df["tags"].apply(len)
    # 技巧 B: 因為 CSV 不適合存 Python 串列 (List)，我們把 ['life', 'love'] 轉成 "life, love" 字串
    df["tags"] = df["tags"].apply(lambda x: ", ".join(x))

    # 4. 儲存成csv檔案
    output_path = Path("quotes.json_cleaned.csv")
    df.to_csv(
        output_path, index=False, encoding="utf-8-sig"
    )  # utf-8-sig 確保 Excel 打開不會亂碼

    return {
        "status": "成功",
        "message": f"資料已成功清洗並儲存至{output_path.resolve()}",
        "data_summary": {
            "total_rows": len(df),
            "columns": list(df.columns),
            "average_tags_per_quote": float(df["tag_count"].mean()),  # 計算平均標籤
        },
    }


# 建立 API 路由，允許使用者決定要爬取幾頁
@app.get("/api/quotes")
async def get_quotes(
    start_page: int = Query(1, description="開始頁數", ge=1),
    end_page: int = Query(3, description="結束頁數", ge=1),
):
    """
    非同步爬取指定頁數的名言，並回傳 JSON 資料
    """
    if end_page < start_page:
        return {"error": "結束頁數不能小於開始頁數"}

    async with httpx.AsyncClient() as client:
        # 動態產生任務清單
        tasks = [fetch_page(client, page) for page in range(start_page, end_page + 1)]

        # 同時執行所有網路請求
        pages_html = await asyncio.gather(*tasks)

        all_results = []
        for html in pages_html:
            all_results.extend(parse_quotes(html))

        return {
            "total_scraped": len(all_results),
            "pages": f"{start_page} ~ {end_page}",
            "data": all_results,
        }


if __name__ == "__main__":
    import uvicorn

    # 啟動 FastAPI 伺服器
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
