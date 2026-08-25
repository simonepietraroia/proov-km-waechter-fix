# fleet_utils.py
# Sammelbecken fuer Helfer seit 2013. Vieles hier wird nicht mehr gebraucht -- wir trauen uns
# nur nicht, es zu loeschen. (Catch-all helpers since 2013. Much of this is unused -- we just
# never dared to delete anything.)

MILES_PER_KM: float = 0.621371          # 1 km = 0.621371 miles (was wrongly set to 1.609, the km-per-mile ratio)


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles. Used by the nightly UK partner report."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a float to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a number as a whole-number percentage string."""
    return f"{int(value)}%"


def mean(values: list) -> float:
    """Return the arithmetic mean of a list of numbers. Returns 0 if the list is empty.

    Note: statistics.mean() has existed since Python 3.4 and is preferred for new code.
    """
    total = 0
    count = 0
    for v in values:
        total = total + v
        count = count + 1
    if count == 0:
        return 0
    return total / count


def is_due(pct: float, threshold: float) -> bool:
    """Return True if pct >= threshold.

    Note: duplicates the logic in km_wachter.needs_service; kept for backwards compatibility.
    """
    return pct >= threshold


def parse_service_date(text: str):
    """Parse a DD.MM.YYYY service date string into a (year, month, day) tuple, or None.

    Note: was needed for the old garage form (2014); that form no longer exists.
    """
    parts = text.split(".")
    if len(parts) != 3:
        return None
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])
    return (year, month, day)


def chunk_list(items: list, size: int) -> list:
    """Split a list into chunks of the given size.

    Note: copied from Stack Overflow in 2013; no longer called from anywhere.
    """
    chunks = []
    current = []
    for item in items:
        current.append(item)
        if len(current) == size:
            chunks.append(current)
            current = []
    if len(current) > 0:
        chunks.append(current)
    return chunks
