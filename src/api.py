import json
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from src.schemas import PredictRequest, PredictResponse
from src.features import add_time_features, add_distance, add_clusters, flag

app = FastAPI(title="NYC Taxi Duration API", version="1.0")

# --- загрузка артефактов при старте ---
MODEL_PATH = "artifacts/model.joblib"
KMEANS_PATH = "artifacts/kmeans.joblib"
FEATURES_PATH = "artifacts/feature_cols.json"

# --- загрузка моделей ---
model = joblib.load(MODEL_PATH)
kmeans = joblib.load(KMEANS_PATH)

# берем только используемые признаки из файла
with open(FEATURES_PATH, "r", encoding="utf-8") as f:
    feature_cols = json.load(f)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    # 1) вход → DataFrame из 1 строки
    df = pd.DataFrame([req.model_dump()])


    # 3) feature engineering
    df = add_time_features(df)
    df = add_distance(df)
    df = add_clusters(df, kmeans)
    df = flag(df)


    # 4) собрать матрицу признаков в нужном порядке
    X = df.reindex(columns=feature_cols)

    # 5) предсказание (предположим модель обучалась на log1p(duration))
    pred_log = model.predict(X)[0]
    pred_seconds = float(np.expm1(pred_log))
    pred_seconds = max(0.0, pred_seconds)

    return PredictResponse(
        trip_duration_seconds=pred_seconds,
        trip_duration_minutes=pred_seconds / 60.0
    )