from pydantic import BaseModel, Field
from datetime import datetime


# --- схемы для api.py ---
class PredictRequest(BaseModel):
    pickup_datetime: datetime

    pickup_latitude: float
    pickup_longitude: float
    dropoff_latitude: float
    dropoff_longitude: float

    passenger_count: int = Field(ge=1, le=6)
    vendor_id: int = Field(default=1)
    store_and_fwd_flag: str = Field(default="N")  # "Y" или "N"

class PredictResponse(BaseModel):
    trip_duration_seconds: float
    trip_duration_minutes: float