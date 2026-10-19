import os
import random
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.model import ModelService
from app.schemas import SleepDataInput, PredictionResponse

# Root directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(
    title="Digital Insomnia & Sleep Debt ANN Predictor",
    description="FastAPI Backend for PyTorch ANN Model classifying Sleep Debt from Digital Insomnia factors.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Model Service
model_service = ModelService(base_dir=BASE_DIR)

# Mount static directory for frontend assets
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Digital Insomnia API is running. Frontend static/index.html not found."}

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model_service.model is not None,
        "classes": model_service.target_mappings
    }

@app.post("/api/predict", response_model=PredictionResponse)
def predict_sleep_debt(payload: SleepDataInput):
    try:
        input_data = payload.model_dump()
        result = model_service.predict(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/api/presets")
def get_presets():
    """
    Returns curated preset profiles representing different sleep debt levels.
    """
    return {
        "no_debt": {
            "title": "Optimal & Sağlıklı Uyku",
            "description": "Erken yatan, yatmadan önce minimum ekran kullanan, mavi ışık filtresi açık ve yüksek uyku kalitesi olan profil.",
            "data": {
                "age": 28,
                "gender": "Female",
                "chronotype": "Early Bird",
                "occupation": "Professional",
                "bedtime_hour": 22.5,
                "screen_time_before_bed_min": 15.0,
                "primary_app_category": "E-Reading",
                "screen_brightness_pct": 30.0,
                "blue_light_filter_on": True,
                "caffeine_intake_mg": 40.0,
                "caffeine_last_hour": 12.0,
                "physical_activity_min": 60.0,
                "room_temperature_f": 66.0,
                "ambient_noise_db": 25.0,
                "sleep_onset_latency_min": 15.0,
                "total_sleep_hours": 8.0,
                "rem_sleep_pct": 21.0,
                "deep_sleep_pct": 22.0,
                "awakenings_count": 0,
                "sleep_efficiency_pct": 94.0,
                "next_day_fatigue_score": 2.1
            }
        },
        "mild_debt": {
            "title": "Hafif Uyku Borcu",
            "description": "Orta düzeyde akşam ekran kullanımı, gece geç saatte kahve ve bölünmüş uyku içeren tipik öğrenci/çalışan profili.",
            "data": {
                "age": 26,
                "gender": "Male",
                "chronotype": "Intermediate",
                "occupation": "Student",
                "bedtime_hour": 23.8,
                "screen_time_before_bed_min": 65.0,
                "primary_app_category": "Messaging",
                "screen_brightness_pct": 65.0,
                "blue_light_filter_on": True,
                "caffeine_intake_mg": 120.0,
                "caffeine_last_hour": 17.5,
                "physical_activity_min": 25.0,
                "room_temperature_f": 70.0,
                "ambient_noise_db": 38.0,
                "sleep_onset_latency_min": 32.0,
                "total_sleep_hours": 6.6,
                "rem_sleep_pct": 16.5,
                "deep_sleep_pct": 17.0,
                "awakenings_count": 2,
                "sleep_efficiency_pct": 82.0,
                "next_day_fatigue_score": 5.2
            }
        },
        "moderate_debt": {
            "title": "Orta / Yüksek Dijital Uykusuzluk",
            "description": "Gece geç saatlere kadar yüksek parlaklıkta kısa video/sosyal medya tüketimi, yüksek kafein ve düşük uyku kalitesi.",
            "data": {
                "age": 23,
                "gender": "Female",
                "chronotype": "Night Owl",
                "occupation": "Student",
                "bedtime_hour": 1.5,
                "screen_time_before_bed_min": 120.0,
                "primary_app_category": "Short-Form Video",
                "screen_brightness_pct": 95.0,
                "blue_light_filter_on": False,
                "caffeine_intake_mg": 280.0,
                "caffeine_last_hour": 21.0,
                "physical_activity_min": 10.0,
                "room_temperature_f": 74.0,
                "ambient_noise_db": 46.0,
                "sleep_onset_latency_min": 55.0,
                "total_sleep_hours": 5.0,
                "rem_sleep_pct": 13.0,
                "deep_sleep_pct": 12.0,
                "awakenings_count": 6,
                "sleep_efficiency_pct": 68.0,
                "next_day_fatigue_score": 8.4
            }
        }
    }

@app.get("/api/random-sample")
def get_random_sample():
    """
    Returns a real random record from sleep_debt_screen_time.csv
    along with its ground truth label for demonstration and verification.
    """
    csv_path = os.path.join(BASE_DIR, "sleep_debt_screen_time.csv")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Dataset CSV not found")

    # Read a random sample
    # Randomly pick an index
    total_rows = 8500
    skip = random.randint(1, total_rows - 5)
    df = pd.read_csv(csv_path, skiprows=range(1, skip), nrows=1)
    row = df.iloc[0].to_dict()
    
    actual_label = row.pop("sleep_debt_category", None)
    user_id = row.pop("user_id", None)
    
    # Cast types properly
    row["blue_light_filter_on"] = bool(row["blue_light_filter_on"])
    row["awakenings_count"] = int(row["awakenings_count"])

    return {
        "user_id": user_id,
        "actual_label": actual_label,
        "data": row
    }
