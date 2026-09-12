from datetime import datetime, timedelta
from pathlib import Path
import random
import pandas as pd

DATA = Path(__file__).resolve().parent / "data" / "fare_observations.csv"

# Controlled demonstration dataset. In production, replace these rows with
# observations returned by an authorized airline/GDS/OTA data source.
# 50 representative routes × 6 booking-window snapshots = 300 observations.
ROUTES = [
    ('DEL', 'BOM', '6E', '6E-DEMO2042', 5200, 0.05714285714285714),
    ('DEL', 'BLR', 'AI', 'AI-DEMO803', 6100, 0.05523809523809524),
    ('BOM', 'DEL', '6E', '6E-DEMO1187', 5100, 0.05238095238095238),
    ('DEL', 'HYD', '6E', '6E-DEMO417', 4700, 0.04952380952380952),
    ('DEL', 'MAA', 'AI', 'AI-DEMO542', 5600, 0.04666666666666667),
    ('BOM', 'BLR', '6E', '6E-DEMO621', 4900, 0.043809523809523805),
    ('DEL', 'CCU', 'AI', 'AI-DEMO764', 5900, 0.04095238095238095),
    ('BOM', 'HYD', '6E', '6E-DEMO931', 4300, 0.03809523809523809),
    ('BLR', 'MAA', '6E', '6E-DEMO287', 3900, 0.035238095238095235),
    ('DEL', 'GOI', 'AI', 'AI-DEMO219', 6500, 0.03333333333333333),
    ('DEL', 'AMD', '6E', '6E-DEMO331', 4400, 0.03142857142857143),
    ('BOM', 'CCU', 'AI', 'AI-DEMO476', 6200, 0.02952380952380952),
    ('DEL', 'PNQ', '6E', '6E-DEMO582', 4100, 0.02761904761904762),
    ('BLR', 'DEL', '6E', '6E-DEMO694', 6000, 0.025714285714285714),
    ('HYD', 'BLR', 'AI', 'AI-DEMO721', 4500, 0.023809523809523808),
    ('MAA', 'DEL', '6E', '6E-DEMO833', 5700, 0.022857142857142857),
    ('DEL', 'COK', 'AI', 'AI-DEMO904', 6800, 0.021904761904761903),
    ('BOM', 'GOI', '6E', '6E-DEMO145', 3600, 0.02),
    ('DEL', 'JAI', '6E', '6E-DEMO258', 3800, 0.019047619047619046),
    ('BLR', 'HYD', 'AI', 'AI-DEMO367', 4000, 0.018095238095238095),
    ('BOM', 'AMD', '6E', '6E-DEMO479', 4200, 0.01714285714285714),
    ('DEL', 'LKO', 'AI', 'AI-DEMO518', 3500, 0.016190476190476193),
    ('HYD', 'DEL', '6E', '6E-DEMO629', 4800, 0.015238095238095238),
    ('CCU', 'DEL', 'AI', 'AI-DEMO741', 6100, 0.014285714285714285),
    ('BLR', 'GOI', '6E', '6E-DEMO852', 3700, 0.013333333333333332),
    ('BOM', 'MAA', '6E', '6E-DEMO901', 5200, 0.01238095238095238),
    ('DEL', 'SXR', 'AI', 'AI-DEMO902', 7200, 0.01238095238095238),
    ('DEL', 'PAT', '6E', '6E-DEMO903', 4200, 0.011428571428571429),
    ('DEL', 'IXC', '6E', '6E-DEMO904', 3900, 0.011428571428571429),
    ('DEL', 'GAU', 'AI', 'AI-DEMO905', 6800, 0.011428571428571429),
    ('BOM', 'COK', '6E', '6E-DEMO906', 5700, 0.010476190476190476),
    ('BOM', 'PNQ', '6E', '6E-DEMO907', 3900, 0.010476190476190476),
    ('BOM', 'JAI', 'AI', 'AI-DEMO908', 5300, 0.010476190476190476),
    ('BLR', 'COK', '6E', '6E-DEMO909', 4400, 0.009523809523809523),
    ('BLR', 'CCU', 'AI', 'AI-DEMO910', 6100, 0.009523809523809523),
    ('HYD', 'MAA', '6E', '6E-DEMO911', 4000, 0.009523809523809523),
    ('HYD', 'CCU', 'AI', 'AI-DEMO912', 5600, 0.009523809523809523),
    ('MAA', 'BOM', '6E', '6E-DEMO913', 5100, 0.009523809523809523),
    ('MAA', 'BLR', '6E', '6E-DEMO914', 3900, 0.00857142857142857),
    ('CCU', 'BOM', 'AI', 'AI-DEMO915', 6000, 0.00857142857142857),
    ('CCU', 'BLR', '6E', '6E-DEMO916', 5800, 0.00857142857142857),
    ('GOI', 'DEL', 'AI', 'AI-DEMO917', 6400, 0.00857142857142857),
    ('GOI', 'BOM', '6E', '6E-DEMO918', 3500, 0.007619047619047619),
    ('AMD', 'DEL', '6E', '6E-DEMO919', 4400, 0.007619047619047619),
    ('AMD', 'BOM', 'AI', 'AI-DEMO920', 4500, 0.007619047619047619),
    ('COK', 'DEL', '6E', '6E-DEMO921', 6700, 0.007619047619047619),
    ('COK', 'BLR', 'AI', 'AI-DEMO922', 4300, 0.007619047619047619),
    ('JAI', 'DEL', '6E', '6E-DEMO923', 3900, 0.007619047619047619),
    ('LKO', 'DEL', 'AI', 'AI-DEMO924', 3700, 0.006666666666666666),
    ('PAT', 'DEL', '6E', '6E-DEMO925', 4100, 0.006666666666666666),
]

# Six snapshots give a richer booking-window curve while keeping exactly 300 rows.
LEAD_TIMES = [45, 30, 21, 15, 7, 1]


def collect_mock_data():
    # Deliberately vary every collection run so a browser refresh demonstrates
    # a changing market index. A production collector would use source data.
    rng = random.Random()
    today = datetime.now().date()
    collected_at = datetime.now().isoformat(timespec="seconds")
    rows = []

    for i, (origin, destination, airline, flight_no, base, weight) in enumerate(ROUTES):
        departure = today + timedelta(days=45)
        route_bias = 1 + ((i % 7) - 3) * 0.008

        for lead in LEAD_TIMES:
            lead_factor = 1 + (45 - lead) * 0.0025
            noise = rng.uniform(0.975, 1.025)
            shock = 1.0
            if lead == 1 and i in {0, 3, 8, 14, 21}:
                shock = {0: 1.055, 3: 1.035, 8: 1.065, 14: 1.045, 21: 1.050}[i]
            fare = base * lead_factor * route_bias * noise * shock
            rows.append({
                "source": "DEMO_AUTHORIZED_API",
                "origin": origin,
                "destination": destination,
                "airline": airline,
                "flight_no": flight_no,
                "departure_date": departure.isoformat(),
                "lead_time_days": lead,
                "fare_class": "ECONOMY",
                "base_fare": round(fare * 0.78, 2),
                "taxes": round(fare * 0.22, 2),
                "total_fare": round(fare, 2),
                "currency": "INR",
                "collected_at": collected_at,
            })

    df = pd.DataFrame(rows)
    DATA.parent.mkdir(exist_ok=True)
    df.to_csv(DATA, index=False)
    return df


if __name__ == "__main__":
    df = collect_mock_data()
    print(f"Collected {len(df)} observations and saved to {DATA}")
