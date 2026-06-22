import fastf1
import json

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