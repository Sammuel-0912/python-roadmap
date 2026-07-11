from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from transformers import pipeline

# 建立一個全域變數來存放我們的 AI 模型
# 這樣可以讓不同的 API 路由共享同一個模型實例，避免重複載入浪費記憶體
ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan 管理器：在 FastAPI 伺服器啟動與關閉時執行的邏輯。
    這是現代 FastAPI（0.93.0+）推薦的模型載入方式。
    """
    print("🤖 [Lifespan] 正在載入 Hugging Face 情感分析模型...")
    # 在伺服器啟動時，一次性將模型載入記憶體
    ml_models["sentiment_analyzer"] = pipeline(
        "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english"
    )
    print("✅ [Lifespan] AI 模型載入成功，伺服器準備就緒！")

    yield  # 伺服器運作期間會停在這裡

    # 伺服器關閉時執行的清理邏輯
    print("🧹 [Lifespan] 正在關閉伺服器，釋放資源...")
    ml_models.clear()


# 將 lifespan 掛載到 FastAPI 應用中
app = FastAPI(title="AI情感分析 API服務", version="3.0", lifespan=lifespan)


@app.get("/api/predict")
async def predict_sentiment(
    text: str = Query(
        ..., description="要進行情感分析的英文句子", min_length=1, max_length=500
    )
):
    """
    即時 AI 情感分析路由
    使用者輸入一句英文，API 會立刻經由 AI 模型計算並回傳正負向與信心度。
    """
    classifier = ml_models.get("sentiment_analyzer")
    if not classifier:
        raise HTTPException(status_code=500, detail="AI模型尚未準備就緒")

    try:
        # 呼叫 AI 模型進行預測
        # 雖然 Hugging Face pipeline 底層是同步阻塞的，但對於輕量型的 DistilBERT，
        # 在單次預測時速度極快（通常小於 50 毫秒），因此可直接在路由中安全調用。
        prediction = classifier(text)[0]

        return {
            "status": "success",
            "input_text": text,
            "prediction": {
                "sentiment": prediction["label"],  # POSITIVE 或 NEGATIVE
                "confidence_score": round(
                    prediction["score"], 2
                ),  # 四捨五入到小數點後2位
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI推論過程發生錯誤:{str(e)}")


if __name__ == "__main__":
    import uvicorn

    # 啟動 FastAPI 伺服器
    uvicorn.run("ai_server:app", host="127.0.0.1", port=8001, reload=True)
