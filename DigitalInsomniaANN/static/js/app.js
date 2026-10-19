// Digital Insomnia ANN - Frontend JavaScript

let cachedPresets = null;
let currentGroundTruth = null;

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
    setupInputListeners();
    fetchPresets();
});

// Setup dynamic helper texts and slider listeners
function setupInputListeners() {
    const bedtimeInput = document.getElementById("bedtime_hour");
    const bedtimeDisplay = document.getElementById("bedtime_display");
    if (bedtimeInput && bedtimeDisplay) {
        bedtimeInput.addEventListener("input", (e) => {
            bedtimeDisplay.textContent = `(${formatDecimalHour(parseFloat(e.target.value) || 0)})`;
        });
    }

    const caffeineInput = document.getElementById("caffeine_last_hour");
    const caffeineDisplay = document.getElementById("caffeine_time_display");
    if (caffeineInput && caffeineDisplay) {
        caffeineInput.addEventListener("input", (e) => {
            caffeineDisplay.textContent = `(${formatDecimalHour(parseFloat(e.target.value) || 0)})`;
        });
    }

    const tempInput = document.getElementById("room_temperature_f");
    const tempDisplay = document.getElementById("temp_celsius");
    if (tempInput && tempDisplay) {
        tempInput.addEventListener("input", (e) => {
            const f = parseFloat(e.target.value) || 70;
            const c = ((f - 32) * 5 / 9).toFixed(1);
            tempDisplay.textContent = `(~${c}°C)`;
        });
    }

    const fatigueInput = document.getElementById("next_day_fatigue_score");
    const fatigueVal = document.getElementById("fatigue_val");
    const fatigueDisplay = document.getElementById("fatigue_display");
    if (fatigueInput && fatigueVal) {
        fatigueInput.addEventListener("input", (e) => {
            const val = parseFloat(e.target.value) || 5;
            fatigueVal.textContent = val.toFixed(1);
            
            let label = "Normal";
            if (val <= 3) label = "Enerjik / Zinde";
            else if (val <= 5) label = "Hafif Yorgunluk";
            else if (val <= 7.5) label = "Belirgin Yorgunluk";
            else label = "Aşırı Tükenmişlik";
            
            if (fatigueDisplay) {
                fatigueDisplay.textContent = `(Skor: ${val.toFixed(1)} / 10 - ${label})`;
            }
        });
    }
}

// Convert decimal hour (e.g. 23.5 or 0.25) to "HH:MM"
function formatDecimalHour(val) {
    if (isNaN(val)) return "00:00";
    val = (val % 24 + 24) % 24;
    const hours = Math.floor(val);
    const minutes = Math.round((val - hours) * 60);
    const hh = String(hours).padStart(2, "0");
    const mm = String(minutes).padStart(2, "0");
    return `${hh}:${mm}`;
}

// Pre-fetch presets from backend
async function fetchPresets() {
    try {
        const res = await fetch("/api/presets");
        if (res.ok) {
            cachedPresets = await res.json();
        }
    } catch (err) {
        console.warn("Could not pre-fetch presets:", err);
    }
}

// Load a predefined preset into form
async function loadPreset(presetKey) {
    if (!cachedPresets) {
        await fetchPresets();
    }

    if (!cachedPresets || !cachedPresets[presetKey]) {
        alert("Preset yüklenemedi.");
        return;
    }

    const data = cachedPresets[presetKey].data;
    populateForm(data);
    
    // Clear ground truth since this is a preset
    currentGroundTruth = null;
    hideGroundTruthBadge();

    // Automatically trigger prediction for instant feedback
    submitPredictionForm();
}

// Load random sample from the Kaggle dataset
async function loadRandomSample() {
    const randomBtn = document.querySelector(".btn-random");
    const originalText = randomBtn.innerHTML;
    randomBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Çekiliyor...';
    randomBtn.disabled = true;

    try {
        const res = await fetch("/api/random-sample");
        if (!res.ok) throw new Error("Örnek veri çekilemedi");
        const json = await res.json();
        
        populateForm(json.data);
        
        // Show ground truth badge
        currentGroundTruth = json.actual_label;
        showGroundTruthBadge(json.actual_label, json.user_id);

        // Run prediction
        submitPredictionForm();
    } catch (err) {
        alert("Veri setinden rastgele örnek alınırken hata oluştu: " + err.message);
    } finally {
        randomBtn.innerHTML = originalText;
        randomBtn.disabled = false;
    }
}

function showGroundTruthBadge(actualLabel, userId) {
    const badge = document.getElementById("ground-truth-badge");
    const text = document.getElementById("ground-truth-text");
    if (badge && text) {
        const trMap = {
            "No Debt": "Borç Yok",
            "Mild": "Hafif Borç",
            "Moderate": "Orta Borç",
            "Severe": "Ağır Borç"
        };
        const trLabel = trMap[actualLabel] || actualLabel;
        text.textContent = `${trLabel} (Kullanıcı #${userId})`;
        badge.classList.remove("d-none");
    }
}

function hideGroundTruthBadge() {
    const badge = document.getElementById("ground-truth-badge");
    if (badge) badge.classList.add("d-none");
}

// Populate form inputs with data object
function populateForm(data) {
    for (const [key, value] of Object.entries(data)) {
        const el = document.getElementById(key);
        if (!el) continue;

        if (el.type === "checkbox") {
            el.checked = Boolean(value);
        } else {
            el.value = value;
            el.dispatchEvent(new Event("input"));
        }
    }
}

// Reset form
function resetForm() {
    document.getElementById("sleep-prediction-form").reset();
    document.getElementById("next_day_fatigue_score").dispatchEvent(new Event("input"));
    document.getElementById("bedtime_hour").dispatchEvent(new Event("input"));
    document.getElementById("caffeine_last_hour").dispatchEvent(new Event("input"));
    document.getElementById("room_temperature_f").dispatchEvent(new Event("input"));
    
    hideGroundTruthBadge();
    document.getElementById("results-panel").classList.add("d-none");
    document.getElementById("results-placeholder").classList.remove("d-none");
}

function submitPredictionForm() {
    const form = document.getElementById("sleep-prediction-form");
    if (form) {
        form.requestSubmit();
    }
}

// Handle Form Submission
async function handlePrediction(event) {
    event.preventDefault();

    const submitBtn = document.getElementById("submit-btn");
    const btnText = submitBtn.querySelector(".btn-text");
    const btnLoading = submitBtn.querySelector(".btn-loading");

    // Gather form data
    const formData = new FormData(event.target);
    const payload = {
        age: parseFloat(formData.get("age")),
        gender: formData.get("gender"),
        chronotype: formData.get("chronotype"),
        occupation: formData.get("occupation"),
        
        bedtime_hour: parseFloat(formData.get("bedtime_hour")),
        screen_time_before_bed_min: parseFloat(formData.get("screen_time_before_bed_min")),
        primary_app_category: formData.get("primary_app_category"),
        screen_brightness_pct: parseFloat(formData.get("screen_brightness_pct")),
        blue_light_filter_on: document.getElementById("blue_light_filter_on").checked,
        
        caffeine_intake_mg: parseFloat(formData.get("caffeine_intake_mg")),
        caffeine_last_hour: parseFloat(formData.get("caffeine_last_hour")),
        physical_activity_min: parseFloat(formData.get("physical_activity_min")),
        room_temperature_f: parseFloat(formData.get("room_temperature_f")),
        ambient_noise_db: parseFloat(formData.get("ambient_noise_db")),
        
        sleep_onset_latency_min: parseFloat(formData.get("sleep_onset_latency_min")),
        total_sleep_hours: parseFloat(formData.get("total_sleep_hours")),
        rem_sleep_pct: parseFloat(formData.get("rem_sleep_pct")),
        deep_sleep_pct: parseFloat(formData.get("deep_sleep_pct")),
        awakenings_count: parseInt(formData.get("awakenings_count")),
        sleep_efficiency_pct: parseFloat(formData.get("sleep_efficiency_pct")),
        next_day_fatigue_score: parseFloat(formData.get("next_day_fatigue_score"))
    };

    // UI Loading state
    submitBtn.disabled = true;
    btnText.classList.add("d-none");
    btnLoading.classList.remove("d-none");

    try {
        const response = await fetch("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Tahmin servisi hata döndürdü.");
        }

        const result = await response.json();
        renderResults(result, payload);

    } catch (err) {
        alert("Tahmin yapılırken hata oluştu: " + err.message);
    } finally {
        submitBtn.disabled = false;
        btnText.classList.remove("d-none");
        btnLoading.classList.add("d-none");
    }
}

// Render Results to UI
function renderResults(result, inputs) {
    document.getElementById("results-placeholder").classList.add("d-none");
    const panel = document.getElementById("results-panel");
    panel.classList.remove("d-none");

    const badge = document.getElementById("prediction-badge");
    const title = document.getElementById("prediction-title");
    const icon = document.getElementById("prediction-icon");
    const confVal = document.getElementById("confidence-val");

    badge.className = "prediction-pill"; // reset

    if (result.prediction === "No Debt") {
        badge.classList.add("pill-no-debt");
        icon.className = "fa-solid fa-circle-check";
        title.textContent = "Uyku Borcu Yok (Optimal)";
    } else if (result.prediction === "Mild") {
        badge.classList.add("pill-mild");
        icon.className = "fa-solid fa-triangle-exclamation";
        title.textContent = "Hafif Uyku Borcu (Mild)";
    } else {
        badge.classList.add("pill-moderate");
        icon.className = "fa-solid fa-fire-flame-curved";
        title.textContent = "Orta / Belirgin Uyku Borcu";
    }

    confVal.textContent = `%${result.confidence.toFixed(1)}`;

    // Probabilities
    const probs = result.probabilities || {};
    const noDebtProb = (probs["No Debt"] || 0) * 100;
    const mildProb = (probs["Mild"] || 0) * 100;
    const moderateProb = (probs["Moderate"] || 0) * 100;

    document.getElementById("prob-no-debt-val").textContent = `%${noDebtProb.toFixed(1)}`;
    document.getElementById("prob-no-debt-bar").style.width = `${noDebtProb}%`;

    document.getElementById("prob-mild-val").textContent = `%${mildProb.toFixed(1)}`;
    document.getElementById("prob-mild-bar").style.width = `${mildProb}%`;

    document.getElementById("prob-moderate-val").textContent = `%${moderateProb.toFixed(1)}`;
    document.getElementById("prob-moderate-bar").style.width = `${moderateProb}%`;

    // Render personalized insights
    generateInsights(inputs, result);

    // Smooth scroll to results on mobile
    if (window.innerWidth <= 1024) {
        panel.scrollIntoView({ behavior: "smooth" });
    }
}

// Generate intelligent hygiene insights based on inputs
function generateInsights(inputs, result) {
    const list = document.getElementById("insights-list");
    list.innerHTML = "";

    const insights = [];

    // Screen time insight
    if (inputs.screen_time_before_bed_min > 60) {
        insights.push({
            icon: "fa-mobile-screen",
            text: `Yatmadan önceki ekran süreniz (${inputs.screen_time_before_bed_min} dk) melatonin salgılanmasını geciktiriyor. Yatak öncesi 30 dakikanın altına indirmeyi hedefleyin.`
        });
    }

    // Blue light insight
    if (!inputs.blue_light_filter_on && inputs.screen_time_before_bed_min > 20) {
        insights.push({
            icon: "fa-eye-slash",
            text: "Mavi ışık filtresi kapalı! Akşam saatlerinde ekran sıcaklığını (Night Shift / Mavi Işık Filtresi) açarak göz ve sirkadiyen ritim yorgunluğunu azaltabilirsiniz."
        });
    }

    // Bedtime hour insight
    if (inputs.bedtime_hour > 0 && inputs.bedtime_hour < 5) {
        insights.push({
            icon: "fa-clock",
            text: `Gece 0${Math.floor(inputs.bedtime_hour)} civarında yatmanız biyolojik onarım saatlerini kaçırmanıza yol açıyor.`
        });
    }

    // Caffeine timing
    if (inputs.caffeine_last_hour >= 18.0) {
        insights.push({
            icon: "fa-mug-hot",
            text: `Saat ${formatDecimalHour(inputs.caffeine_last_hour)}'deki son kafein alımı derin uyku fazını baskılıyor. Kafein tüketimini yatmadan en az 6 saat önce sonlandırın.`
        });
    }

    // Sleep duration
    if (inputs.total_sleep_hours < 6.5) {
        insights.push({
            icon: "fa-hourglass-half",
            text: `Gecelik toplam ${inputs.total_sleep_hours.toFixed(1)} saat uyku, kümülatif dijital uyku borcunun ana kaynağıdır. Minimum 7-8 saat aralığını hedefleyin.`
        });
    }

    // Sleep Latency
    if (inputs.sleep_onset_latency_min > 30) {
        insights.push({
            icon: "fa-bed",
            text: `Uykuya dalma süreniz (${inputs.sleep_onset_latency_min} dk) normalin üzerinde. Yatmadan önce parlaklığı ve dopaminerjik kısa video tüketimini sınırlandırmak dalış süresini kısaltacaktır.`
        });
    }

    // Positive reinforcement if profile is great
    if (insights.length === 0) {
        insights.push({
            icon: "fa-circle-check",
            text: "Harika uyku hijyeni! Ekran süresi, yatış saati ve uyku mimarisi değerleriniz ideal referans aralıklarında seyrediyor."
        });
    }

    insights.forEach(item => {
        const li = document.createElement("li");
        li.innerHTML = `<i class="fa-solid ${item.icon}"></i> <span>${item.text}</span>`;
        list.appendChild(li);
    });
}
