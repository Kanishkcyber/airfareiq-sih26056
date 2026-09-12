# AirfareIQ — Real Airfare Price Index (SIH26056)

Presentation-ready local prototype for SIH 2026 Problem Statement SIH26056.

## What is included
- Professional minimal dashboard with working sidebar views
- 150 controlled demonstration fare observations
- 10-route traffic-weighted demonstration basket
- T+45, T+30, T+15, T+7 and T+1 booking-window series
- Route performance and anomaly monitor
- FastAPI backend and collection button
- Transparent index formula: AI_t = 100 × Σ w_r(F_r,t / F_r,0)

## Run
```powershell
python -m pip install -r requirements.txt
python collector.py
python -m uvicorn app:app --reload
```
Then open `http://127.0.0.1:8000`.

## Important demo note
The collector currently generates controlled demonstration data. It does **not** claim to be a live airfare feed. For deployment, replace `collect_mock_data()` with an authorized airline, GDS or OTA API connector and retain the same validation/index/dashboard pipeline.

The route weights in `routes.csv` are demonstration weights showing the intended traffic-weighting mechanism; they should be replaced with the project's validated DGCA traffic dataset for a production index.


## Demo refresh behavior
Each dashboard load generates a fresh controlled 150-row snapshot (25 routes × 6 booking-window lead times), so the displayed index can change after browser refresh. This is demonstration behavior; production deployment should read live observations from authorized sources.
