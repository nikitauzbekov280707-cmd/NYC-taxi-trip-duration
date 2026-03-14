import numpy as np
import pandas as pd

# функция для нахождения расстояниями между двумя точками на земной плоскости
def haversine_km(lon1, lat1, lon2, lat2) -> float:
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return float(6371 * c)

# функция для создания временных признаков
def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    dt = pd.to_datetime(df["pickup_datetime"])
    df = df.copy()
    df["pickup_hour"] = dt.dt.hour
    df["pickup_dow"] = dt.dt.dayofweek
    df["pickup_month"] = dt.dt.month
    df["pickup_is_weekend"] = (df["pickup_dow"] >= 5).astype(int)
    return df

# функция для добавления дистанции
def add_distance(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["distance_km"] = [
        haversine_km(lo1, la1, lo2, la2)
        for lo1, la1, lo2, la2 in zip(
            df["pickup_longitude"], df["pickup_latitude"],
            df["dropoff_longitude"], df["dropoff_latitude"]
        )
    ]
    return df

# добавляем кластеры для новых данных на ранее обученной модели
def add_clusters(df: pd.DataFrame, kmeans) -> pd.DataFrame:
    df = df.copy()
    df["pickup_cluster"] = kmeans.predict(df[["pickup_latitude", "pickup_longitude"]])
    df["dropoff_cluster"] = kmeans.predict(df[["dropoff_latitude", "dropoff_longitude"]])
    return df

# переводим значение флага в числовой вид
def flag(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "store_and_fwd_flag" in df:
        df["store_and_fwd_flag"] = df["store_and_fwd_flag"].map({"N": 0, "Y": 1}).astype("int8")
        return df

