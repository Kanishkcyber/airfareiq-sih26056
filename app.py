from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
import pandas as pd
from collector import collect_mock_data
from index_engine import calculate_index, lead_time_series, load_data

BASE = Path(__file__).resolve().parent
app = FastAPI(title="Real Airfare Price Index — SIH26056")
INDEX_HISTORY = []
HTML = (BASE / "static" / "index.html").read_text(encoding="utf-8")

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.get("/api/dashboard")
def dashboard():
    # Demo mode: generate a fresh market snapshot on every dashboard load so
    # browser refresh visibly changes the index. Production would read live data.
    collect_mock_data()
    idx, route = calculate_index(1)
    data = load_data()
    routes = []
    for _, r in route.iterrows():
        movement = round((r.price_relative - 1) * 100, 2)
        routes.append({
            "route": f"{r.origin} → {r.destination}",
            "origin": r.origin, "destination": r.destination,
            "weight": float(r.route_weight),
            "current_fare": float(r.current_fare),
            "base_fare": float(r.base_fare),
            "movement_pct": movement,
        })
    anomalies = [{
        "route": r["route"], "movement_pct": r["movement_pct"],
        "severity": "HIGH" if abs(r["movement_pct"]) >= 15 else "MEDIUM",
        "message": f"Fare movement of {r['movement_pct']:+.1f}% detected against the 45-day route base."
    } for r in routes if abs(r["movement_pct"]) >= 8]
    last = None if data.empty else str(data["collected_at"].max())
    INDEX_HISTORY.append({"timestamp": last, "index": float(idx)})
    if len(INDEX_HISTORY) > 12:
        del INDEX_HISTORY[:-12]
    return {"national_index": float(idx), "base": 100, "observations": len(data),
            "routes": routes, "lead_time": lead_time_series(), "anomalies": anomalies,
            "last_collected": last}

@app.get("/api/observations")
def observations():
    data = load_data()
    return [] if data.empty else data.fillna("").to_dict(orient="records")

@app.post("/api/collect")
def collect():
    df = collect_mock_data()
    idx, _ = calculate_index(1)
    INDEX_HISTORY.append({"timestamp": str(df.collected_at.max()), "index": float(idx)})
    if len(INDEX_HISTORY) > 12:
        del INDEX_HISTORY[:-12]
    return {"status":"success", "new_observations":len(df),
            "national_index":float(idx), "collected_at":str(df.collected_at.max())}


@app.get("/api/prediction")
def prediction():
    current = calculate_index(1)[0]
    # Demonstration forecast: use recent collected index snapshots when available.
    # If there is not enough temporal history yet, fall back to a damped booking-window
    # pressure signal. This is intentionally labelled as a prototype forecast.
    hist = [float(x["index"]) for x in INDEX_HISTORY if x.get("index") is not None]
    if len(hist) >= 2:
        recent = hist[-min(6, len(hist)):]
        slopes = [recent[i] - recent[i-1] for i in range(1, len(recent))]
        trend = sum(slopes) / len(slopes)
    else:
        series = lead_time_series()
        t7 = next((x["index"] for x in series if x["days"] == 7), current)
        trend = (current - float(t7)) * 0.22
    trend = max(-1.25, min(1.25, trend))
    forecast = [{"label":"Now", "index":round(float(current),2), "band":0.45}]
    value = float(current)
    for i in range(1, 8):
        value += trend * (0.88 ** (i-1))
        band = 0.45 + i * 0.22
        forecast.append({"label":f"P+{i}", "index":round(value,2), "band":round(band,2)})
    return {"forecast": forecast, "history_points": len(hist), "model": "damped trend demonstration"}
