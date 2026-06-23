import fastf1
import json
import numpy as np
from scipy.interpolate import CubicSpline
import pandas as pd

fastf1.Cache.enable_cache("data/.fastf1_cache")

session = fastf1.get_session(2024, "Silverstone", "R")
session.load()

def save_circuit_info(session, race_id):
    circuit_info = session.get_circuit_info()

    circuit_data = {
        "rotation": circuit_info.rotation,
        "corners": [
            {"number": row["Number"], "x": row["X"], "y": row["Y"]}
            for _, row in circuit_info.corners.iterrows()
        ],
    }

    with open(f"data/{race_id}/circuit.json", "w") as f:
        json.dump(circuit_data, f, indent=2)

save_circuit_info(session, "silverstone_2024")
print(session.results[["DriverNumber", "Abbreviation", "FullName"]])

def interpolate_driver_position(session, driver_number):
    pos = session.pos_data[driver_number]
    moving = pos[(pos['X'] != 0) | (pos['Y'] != 0)]

    t = moving['Time'].dt.total_seconds().to_numpy()
    x = moving['X'].to_numpy()
    y = moving['Y'].to_numpy()

    cs_x = CubicSpline(t, x)
    cs_y = CubicSpline(t, y)

    t_grid = np.arange(t[0], t[-1], 0.1)
    x_smooth = cs_x(t_grid)
    y_smooth = cs_y(t_grid)

    return t_grid, x_smooth, y_smooth

def build_positions(session):
    frames = []

    for driver_number in session.drivers:
        t_grid, x_smooth, y_smooth = interpolate_driver_position(session, driver_number)
        driver_code = session.get_driver(driver_number)['Abbreviation']

        frame = pd.DataFrame({
            'time': t_grid,
            'driver': driver_code,
            'x': x_smooth,
            'y': y_smooth,
        })
        frames.append(frame)

    return pd.concat(frames, ignore_index=True)

def extract_driver_telemetry(session, driver_number):
    tel = session.car_data[driver_number]
    driver_code = session.get_driver(driver_number)['Abbreviation']

    return pd.DataFrame({
        'time': tel['Time'].dt.total_seconds(),
        'driver': driver_code,
        'speed': tel['Speed'],
        'throttle': tel['Throttle'],
        'brake': tel['Brake'],
        'gear': tel['nGear'],
        'drs': tel['DRS'],
    })

def build_telemetry(session):
    frames = []

    for driver_number in session.drivers:
        frames.append(extract_driver_telemetry(session, driver_number))

    return pd.concat(frames, ignore_index=True)

build_positions(session).to_parquet("data/silverstone_2024/positions.parquet", index=False)
build_telemetry(session).to_parquet("data/silverstone_2024/telemetry.parquet", index=False)

df = pd.read_parquet("data/silverstone_2024/telemetry.parquet")
print(df.shape)
print(df.head())
print(session.laps[['Driver', 'LapNumber', 'Compound', 'TyreLife', 'Stint']].head(20))