import sys
from pathlib import Path
import matplotlib

# Windows 終端機預設用 cp950，無法印出 emoji，強制改用 UTF-8 輸出
sys.stdout.reconfigure(encoding="utf-8")

# 這支腳本只把圖表存成 PNG，不需要開視窗，改用 Agg 後端可避免 venv 找不到 Tcl/Tk 的錯誤
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud

# 設定 Seaborn 與 Matplotlib 的主題風格
sns.set_theme(style="whitegrid")
# 解決 matplotlib 中文顯示問題（若未來有中文資料需求）
plt.rcParams["font.family"] = ["Arial"]


def load_data(file_path: str) -> pd.DataFrame:
    """讀取 CSV 檔案並進行基本確認"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"找不到檔案 {file_path} 請確認是否已執行過 FastAPI 儲存 CSV的路由!"
        )
    df = pd.read_csv(path)
    print(f"✅成功載入資料!共有{len(df)}筆名言。")
    return df


def plot_top_authors(df: pd.DataFrame, output_image: str):
    """分析前 5 大多產作者並繪製長條圖"""
    # 使用 Pandas 的 value_counts() 快速統計各作者出現次數，並取前 5 名
    top_authors = df["author"].value_counts().head(5)

    print("\n📊 數據分析 - 前5大多產作者:")
    print(top_authors)

    # 建立畫布
    plt.figure(figsize=(10, 6))

    # 使用 Seaborn 繪製長條圖 (Barplot)
    sns.barplot(
        x=top_authors.values,
        y=top_authors.index,
        hue=top_authors.index,
        palette="viridis",
        legend=False,
    )

    # 設定圖表標題與標籤
    plt.title("Top 5 Authors by Quote Count", fontsize=16, fontweight="bold")
    plt.xlabel("Number of Quotes", fontsize=12)
    plt.ylabel("Author", fontsize=12)

    # 自動調整排版並儲存圖片
    plt.tight_layout()
    plt.savefig(output_image, dpi=300)
    plt.close()
    print(f"💾 長條圖已經儲存至{output_image}")


def generate_tag_wordcloud(df: pd.DataFrame, output_image: str):
    """將所有標籤（Tags）整合並生成文字雲"""

    # 因為之前的 CSV 格式是 "life, love, inspirational"
    all_tags_series = df["tags"].dropna()
    # 2. 將所有列的標籤用逗號拆開，並整理成一個巨大的文字字串（以空格分隔）
    # 例如：["life", "love", "life"] -> "life love life"
    all_tags_list = []
    for tag_str in all_tags_series:
        tags = [t.strip() for t in tag_str.split(",")]
        all_tags_list.extend(tags)
    text_for_wordcloud = " ".join(all_tags_list)

    # 3. 建立文字雲物件
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="white",
        colormap="plasma",
        max_words=50,
    ).generate(text_for_wordcloud)

    # 4. 繪製並儲存文字雲
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")  # 隱藏座標軸

    plt.tight_layout()
    plt.savefig(output_image, dpi=300)
    plt.close()
    print(f"💾 文字雲已儲存至：{output_image}")


if __name__ == "__main__":
    csv_file = "quotes.json_cleaned.csv"

    try:
        # 1. 載入資料
        data_df = load_data(csv_file)
        # 2. 生成分析圖表
        plot_top_authors(data_df, "top_authors.png")
        generate_tag_wordcloud(data_df, "tag_wordcloud.png")

        print("\n🎉 所有資料科學分析與視覺化已完成")
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
