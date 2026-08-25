# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Nobody has cleaned it up since.

SERVICE_INTERVAL_KM: int = 15000
WARN_AT_PERCENT: int = 80


def wear_percent(km_since_service: float, interval: int) -> float:
    """Return wear as a percentage of one service interval (e.g. 99.3 for 14 900 / 15 000 km)."""
    return km_since_service / interval * 100


def needs_service(car: dict) -> bool:
    """Return True if the car has used >= WARN_AT_PERCENT of its current service interval.

    A missing 'last_service_km' key is treated as unknown history: the car is NOT flagged.
    """
    last = car.get("last_service_km")
    if last is None:
        return False
    km_since = car["odometer"] - last
    return wear_percent(km_since, SERVICE_INTERVAL_KM) >= WARN_AT_PERCENT


def check_fleet(fleet: list) -> list:
    """Return the ids of every car that needs a service, and print a line for each."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
