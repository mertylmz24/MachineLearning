from pydantic import BaseModel, Field
from typing import Literal, Dict

class SleepDataInput(BaseModel):
    age: float = Field(25.0, ge=10, le=100, description="Yaş")
    gender: Literal["Female", "Male", "Non-Binary"] = Field("Female", description="Cinsiyet")
    chronotype: Literal["Early Bird", "Intermediate", "Night Owl"] = Field("Intermediate", description="Kronotip")
    occupation: Literal["Freelancer", "Professional", "Retired", "Student", "Unemployed"] = Field("Student", description="Meslek")
    
    bedtime_hour: float = Field(23.5, ge=0.0, le=24.0, description="Yatış saati (Örn: 23.5 = 23:30)")
    screen_time_before_bed_min: float = Field(60.0, ge=0.0, le=360.0, description="Yatmadan önceki ekran süresi (dakika)")
    primary_app_category: Literal[
        "E-Reading", "Gaming", "Messaging", "News", "Short-Form Video", "Social Media", "Streaming"
    ] = Field("Social Media", description="En çok kullanılan uygulama kategorisi")
    screen_brightness_pct: float = Field(70.0, ge=0.0, le=100.0, description="Ekran parlaklığı (%)")
    blue_light_filter_on: bool = Field(False, description="Mavi ışık filtresi aktif mi?")
    
    caffeine_intake_mg: float = Field(100.0, ge=0.0, le=1000.0, description="Günlük kafein tüketimi (mg)")
    caffeine_last_hour: float = Field(16.0, ge=0.0, le=24.0, description="En son kafein alım saati (24 saat formatı)")
    physical_activity_min: float = Field(30.0, ge=0.0, le=360.0, description="Günlük fiziksel aktivite (dakika)")
    room_temperature_f: float = Field(68.0, ge=50.0, le=90.0, description="Oda sıcaklığı (°F)")
    ambient_noise_db: float = Field(35.0, ge=10.0, le=100.0, description="Ortam gürültü seviyesi (dB)")
    
    sleep_onset_latency_min: float = Field(25.0, ge=0.0, le=180.0, description="Uykuya dalma süresi (dakika)")
    total_sleep_hours: float = Field(7.0, ge=2.0, le=14.0, description="Toplam uyku süresi (saat)")
    rem_sleep_pct: float = Field(18.0, ge=0.0, le=50.0, description="REM uyku yüzdesi (%)")
    deep_sleep_pct: float = Field(18.0, ge=0.0, le=50.0, description="Derin uyku yüzdesi (%)")
    awakenings_count: int = Field(2, ge=0, le=20, description="Gece uyanma sayısı")
    sleep_efficiency_pct: float = Field(85.0, ge=30.0, le=100.0, description="Uyku verimliliği (%)")
    next_day_fatigue_score: float = Field(4.0, ge=1.0, le=10.0, description="Ertesi gün yorgunluk hissi (1-10)")

    class Config:
        json_schema_extra = {
            "example": {
                "age": 24,
                "gender": "Female",
                "chronotype": "Intermediate",
                "occupation": "Student",
                "bedtime_hour": 23.5,
                "screen_time_before_bed_min": 75.0,
                "primary_app_category": "Short-Form Video",
                "screen_brightness_pct": 80.0,
                "blue_light_filter_on": False,
                "caffeine_intake_mg": 150.0,
                "caffeine_last_hour": 18.0,
                "physical_activity_min": 20.0,
                "room_temperature_f": 71.0,
                "ambient_noise_db": 38.0,
                "sleep_onset_latency_min": 35.0,
                "total_sleep_hours": 6.2,
                "rem_sleep_pct": 15.0,
                "deep_sleep_pct": 14.0,
                "awakenings_count": 3,
                "sleep_efficiency_pct": 78.0,
                "next_day_fatigue_score": 6.5
            }
        }

class PredictionResponse(BaseModel):
    prediction: str
    prediction_tr: str
    confidence: float
    probabilities: Dict[str, float]
    class_index: int
