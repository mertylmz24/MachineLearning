# 🌙 Digital Insomnia & Sleep Debt ANN Predictor

Kaggle **Digital Insomnia (Screen Time & Sleep Debt)** veri seti üzerine eğitilmiş PyTorch tabanlı Yapay Sinir Ağı (ANN) modelini çalıştıran FastAPI backend ve modern, duyarlı (responsive) web arayüzü.

---

## 🚀 Proje Yapısı

```text
DigitalInsomniaANN/
│
├── digital_insomnia_nn_model.pth    # Eğitilmiş PyTorch ANN Model Ağırlıkları (state_dict)
├── preprocessor.pkl                 # StandardScaler + OneHotEncoder ColumnTransformer
├── target_mappings.pkl              # Hedef sınıf dönüşümü ({'No Debt': 0, 'Mild': 1, 'Moderate': 2})
├── sleep_debt_screen_time.csv       # Kaggle orijinal veri seti
│
├── app/
│   ├── __init__.py
│   ├── model.py                     # ANN Model mimarisi, artifact yükleyici ve tahmin servisi
│   ├── schemas.py                   # Pydantic girdi doğrulama & API yanıt şemaları
│   └── main.py                      # FastAPI ana uygulaması, CORS, endpointler & statik dosya sunumu
│
├── static/
│   ├── index.html                   # Modern koyu tema, cam efektli (glassmorphism) arayüz
│   ├── css/
│   │   └── style.css                # Koyu mod, neon vurgular, mobil uyumlu stil dosyası
│   └── js/
│       └── app.js                   # Form yönetimi, önceden tanımlı senaryolar, dinamik uyku önerileri
│
├── requirements.txt                 # Gerekli kütüphaneler listesi
├── run.py                           # Sunucuyu tek komutla başlatan script
└── README.md                        # Dokümantasyon
```

---

## 🧠 Model Mimarisi & Özellikler

- **Girdi Boyutu:** 31 Özellik
  - **17 Sayısal/Mantıksal Özellik** (`StandardScaler` ile ölçeklendirilmiş): `age`, `bedtime_hour`, `screen_time_before_bed_min`, `screen_brightness_pct`, `blue_light_filter_on`, `caffeine_intake_mg`, `caffeine_last_hour`, `physical_activity_min`, `room_temperature_f`, `ambient_noise_db`, `sleep_onset_latency_min`, `total_sleep_hours`, `rem_sleep_pct`, `deep_sleep_pct`, `awakenings_count`, `sleep_efficiency_pct`, `next_day_fatigue_score`
  - **14 Kategorik Özellik** (`OneHotEncoder(drop='first')`): `gender`, `chronotype`, `occupation`, `primary_app_category`
- **Gizli Katmanlar:**
  - `Linear(31, 15)` &rarr; `ReLU()`
  - `Linear(15, 15)` &rarr; `ReLU()`
- **Çıktı Katmanı:**
  - `Linear(15, 3)` &rarr; `Softmax()`
- **Hedef Sınıflar:**
  - `0`: **No Debt** (Uyku Borcu Yok / Optimal)
  - `1`: **Mild** (Hafif Uyku Borcu)
  - `2`: **Moderate** (Orta / Belirgin Uyku Borcu)

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Sanal Ortamı Aktif Edin (Opsiyonel):
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Gerekli Paketleri Yükleyin:
```powershell
pip install -r requirements.txt
```

### 3. Uygulamayı Başlatın:
```powershell
python run.py
```
veya doğrudan uvicorn ile:
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Tarayıcıda Açın:
- **Web Arayüzü:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Etkileşimli Swagger API Dokümantasyonu:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🌟 Arayüz Özellikleri

1. **Hazır Profil Senaryoları (Presets):**
   - 🟢 **Sağlıklı Uyku:** Erken yatan, mavi ışık filtresi kullanan, düşük kafeinli profil.
   - 🟡 **Hafif Borç:** Ortalama ekran süresi ve hafif düzensiz uyku profili.
   - 🔴 **Ağır Dijital Uykusuzluk:** Gece geç saatte yüksek parlaklıkta kısa video tüketen profil.
   - 🎲 **Veri Setinden Rastgele Çek:** 8500 satırlık Kaggle veri setinden rastgele bir satır çekerek hem model tahminini hem de kullanıcının gerçek etiketini karşılaştırır.
2. **Kişiselleştirilmiş Akıllı Uyku Hijyeni Önerileri:**
   - Girilen parametrelere göre (örneğin 23:00 sonrası kafein, yatmadan önce yüksek ekran süresi, kapalı mavi ışık filtresi vb.) dinamik sağlık tavsiyeleri üretir.
3. **Olasılık Dağılım Çubukları:**
   - 3 sınıfın her biri için modelin hesapladığı Softmax olasılık yüzdelerini gerçek zamanlı görselleştirir.
