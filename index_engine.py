from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "fare_observations.csv"
WEIGHTS = BASE / "routes.csv"


def load_data():
    if not DATA.exists():
        return pd.DataFrame()
    return pd.read_csv(DATA)


def load_weights():
    return pd.read_csv(WEIGHTS)


def calculate_index(lead_time=1):
    fares = load_data()
    weights = load_weights()
    if fares.empty:
        return 100.0, pd.DataFrame()

    if lead_time is not None:
        fares = fares[fares["lead_time_days"] == lead_time]

    if fares.empty:
        return 100.0, pd.DataFrame()

    # Median representative fare protects the index from individual outliers.
    route = (
        fares.groupby(["origin", "destination"], as_index=False)["total_fare"]
        .median()
        .rename(columns={"total_fare": "current_fare"})
    )

    # The 45-day fare is the demonstration base for each route.
    base = (
        load_data()[load_data()["lead_time_days"] == 45]
        .groupby(["origin", "destination"], as_index=False)["total_fare"]
        .median()
        .rename(columns={"total_fare": "base_fare"})
    )

    route = route.merge(base, on=["origin", "destination"], how="left")
    route = route.merge(weights, on=["origin", "destination"], how="left")
    route["route_weight"] = route["route_weight"].fillna(0)
    route["price_relative"] = route["current_fare"] / route["base_fare"]
    route["contribution"] = route["route_weight"] * route["price_relative"]

    # Re-normalize only over routes actually available in the observation set.
    weight_sum = route["route_weight"].sum()
    if weight_sum > 0:
        route["route_weight"] = route["route_weight"] / weight_sum
        route["contribution"] = route["route_weight"] * route["price_relative"]

    index = 100 * route["contribution"].sum()
    return round(float(index), 2), route


def lead_time_series():
    return [
        {"lead_time": f"T+{x}", "days": x, "index": calculate_index(x)[0]}
        for x in [45, 30, 21, 15, 7, 1]
    ]
