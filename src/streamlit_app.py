import streamlit as st
import requests
from datetime import datetime, date, time
from streamlit_folium import st_folium
import folium

API_URL = "http://127.0.0.1:8000/predict"

st.title("NYC Taxi Trip Duration Predictor")

st.subheader("Введите данные поездки")

NYC_CENTER = (40.7580, -73.9855)  # Таймс-сквер примерно

mode = st.radio("Способ ввода координат", ["Вручную", "На карте"], horizontal=False)

# Храним точки в session_state
if "pickup" not in st.session_state:
    st.session_state.pickup = None
if "dropoff" not in st.session_state:
    st.session_state.dropoff = None

if mode == "На карте":
    colA, colB = st.columns([1, 1])

    with colA:
        st.write("Клик 1 = Pickup, клик 2 = Dropoff")
        if st.button("Сбросить точки"):
            st.session_state.pickup = None
            st.session_state.dropoff = None

    # создаём карту
    m = folium.Map(location=NYC_CENTER, zoom_start=11)

    # если точки уже есть — рисуем маркеры
    if st.session_state.pickup is not None:
        folium.Marker(
            location=st.session_state.pickup,
            tooltip="Pickup",
            icon=folium.Icon(color="green")
        ).add_to(m)

    if st.session_state.dropoff is not None:
        folium.Marker(
            location=st.session_state.dropoff,
            tooltip="Dropoff",
            icon=folium.Icon(color="red")
        ).add_to(m)

    # показываем карту и ловим клики
    out = st_folium(m, height=520, width=None)

    # streamlit-folium кладёт последний клик в out["last_clicked"]
    if out and out.get("last_clicked"):
        lat = out["last_clicked"]["lat"]
        lon = out["last_clicked"]["lng"]

        # логика: первый клик -> pickup, второй -> dropoff
        if st.session_state.pickup is None:
            st.session_state.pickup = (lat, lon)
        elif st.session_state.dropoff is None:
            st.session_state.dropoff = (lat, lon)
        else:
            # если обе точки уже стоят, можно заменить dropoff последним кликом (или pickup)
            st.session_state.dropoff = (lat, lon)

    # выведем текущие значения
    st.write("Pickup:", st.session_state.pickup)
    st.write("Dropoff:", st.session_state.dropoff)

    # координаты для формы/предсказания
    if st.session_state.pickup is not None:
        pickup_lat, pickup_lon = st.session_state.pickup
    else:
        pickup_lat, pickup_lon = NYC_CENTER

    if st.session_state.dropoff is not None:
        dropoff_lat, dropoff_lon = st.session_state.dropoff
    else:
        dropoff_lat, dropoff_lon = (40.6413, -73.7781)  # JFK как дефолт

else:
    # режим ручного ввода
    pickup_lat = st.number_input("Pickup latitude", value=40.7580, format="%.6f")
    pickup_lon = st.number_input("Pickup longitude", value=-73.9855, format="%.6f")
    dropoff_lat = st.number_input("Dropoff latitude", value=40.6413, format="%.6f")
    dropoff_lon = st.number_input("Dropoff longitude", value=-73.7781, format="%.6f")


d = st.date_input("Pickup date", value=date(2016, 3, 14))
t = st.time_input("Pickup time", value=time(8, 30))
passenger_count = st.slider("Passenger count", 1, 6, 1)
vendor_id = st.selectbox("Vendor", [1, 2])
store_and_fwd_flag = st.selectbox("Store and fwd flag", ["N", "Y"])

pickup_dt = datetime.combine(d, t)

if st.button("Predict"):
    payload = {
        "pickup_datetime": pickup_dt.isoformat(),
        "pickup_latitude": pickup_lat,
        "pickup_longitude": pickup_lon,
        "dropoff_latitude": dropoff_lat,
        "dropoff_longitude": dropoff_lon,
        "passenger_count": passenger_count,
        "vendor_id": vendor_id,
        "store_and_fwd_flag": store_and_fwd_flag
    }

    try:
        r = requests.post(API_URL, json=payload, timeout=10)
        r.raise_for_status()
        data = r.json()

        st.success(f"⏱ Прогноз: {data['trip_duration_minutes']:.1f} минут "
                   f"({data['trip_duration_seconds']:.0f} секунд)")
    except Exception as e:
        st.error(f"Ошибка запроса к API: {e}")
        st.write("Проверь, что FastAPI запущен и API_URL правильный.")