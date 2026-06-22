import fastf1

fastf1.Cache.enable_cache("data/.fastf1_cache")

session = fastf1.get_session(2024, "Silverstone", "R")
session.load()

print(session.results[["DriverNumber", "Abbreviation", "FullName"]])