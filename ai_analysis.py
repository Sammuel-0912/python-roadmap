from pathlib import Path
import pandas as pd
from transformers import pipeline


def load_data(file_path: str) -> pd.DataFrame:
    """讀取 CSV 檔案"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"找不到檔案 {file_path}，請確認檔案路徑")
    return pd.read_csv(path)


def analyze_sentiment_with_ai(df: pd.DataFrame) -> pd.DataFrame:
    """利用 Hugging Face 模型對名言進行情感分析"""
    print("🤖 正在載入 Hugging Face 情感分析模型 (預設為 DistilBERT)...")
    # 建立一個情感分析的 pipeline
    # 第一次執行時，系統會自動下載模型（約 268MB），之後就會直接從快取讀取，非常快！
    classifier = pipeline(
        "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english"
    )
    print("🚀 開始進行 AI 情感分析...")

    # 為了避免資料量大時跑太慢，我們可以使用列表推導式配合模型批次處理
    # classifier() 可以直接接收一個 List 的字串

    quotes_list = df["quote"].tolist()
    predictions = classifier(quotes_list)

    # 解析預測結果，拆分出「標籤」與「信心分數」
    sentiment_labels = [pred["label"] for pred in predictions]
    setiment_scores = [pred["score"] for pred in predictions]

    # 將分析結果加回 DataFrame 中
    df["ai_sentiment"] = sentiment_labels
    df["ai_score"] = setiment_scores

    return df


def show_insights(df: pd.DataFrame):
    """找出最正向與最負向的名言"""
    print("\n💡 --- AI 數據洞察結果 ---")
    # 1. 找出最正向的名言 (Label 為 POSITIVE 且 Score 最高)
    positive_quotes = df[df["ai_sentiment"] == "POSITIVE"]
    if not positive_quotes.empty:
        most_positive = positive_quotes.sort_values(
            by="ai_score", ascending=False
        ).iloc[0]
        print(f"\n✨ 【最正向積極的名言】 (AI 信心度: {most_positive['ai_score']:.2%})")
        print(f"👉 \"{most_positive['quote']}\" — 作者: {most_positive['author']}")

        # 2. 找出最負向/悲傷的名言 (Label 為 NEGATIVE 且 Score 最高)
        negative_quotes = df[df["ai_sentiment"] == "NEGATIVE"]
        if not negative_quotes.empty:
            most_negative = negative_quotes.sort_values(
                by="ai_score", ascending=False
            ).iloc[0]
            print(
                f"\n🖤 【最消極悲傷的名言】 (AI 信心度: {most_negative['ai_score']:.2%})"
            )
            print(f"👉 \"{most_negative['quote']}\" — 作者: {most_negative['author']}")


if __name__ == "__main__":
    input_csv = "quotes.json_cleaned.csv"
    output_csv = "quotes_with_ai.csv"

    try:
        # 1. 載入資料
        df = load_data(input_csv)

        # 2. AI 情感分析
        df_analyzed = analyze_sentiment_with_ai(df)

        # 3. 顯示極端情感洞察
        show_insights(df_analyzed)

        # 4. 儲存結果
        df_analyzed.to_csv(output_csv, index=False, encoding="utf-8-sig")
        print(f"\n💾 包含 AI 分析結果的資料已儲存至：{output_csv}")

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
