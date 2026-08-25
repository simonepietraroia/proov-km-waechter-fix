# test_fleet_report.py
from fleet_report import fleet_summary

SAMPLE = [
    {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
    {"id": "VOS-2210", "odometer": 48400, "last_service_km": 45000},
]


def test_summary_counts_due_cars():
    # Only VOS-4471 is nearly worn, so exactly one car is due.
    assert fleet_summary(SAMPLE)["due"] == 1


def test_summary_does_not_crash_on_missing_reading():
    # VOS-7788 has no last_service_km; fleet_summary must not raise and must not flag the car.
    fleet = [
        {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
        {"id": "VOS-7788", "odometer": 92000},
    ]
    result = fleet_summary(fleet)
    assert "average_wear" in result, "fleet_summary should return average_wear"
    assert result["due"] == 1, "only the nearly-worn car should be flagged, not the one with no reading"
