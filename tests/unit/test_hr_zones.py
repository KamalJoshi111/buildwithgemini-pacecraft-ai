# Unit test for calculate_heart_rate_zones tool

from app.agent import calculate_heart_rate_zones


def test_calculate_heart_rate_zones():
    # Test resting_hr = 55, max_hr = 185 (from eval question in project_brief.md)
    # HRR = 130
    # Zone 1: 55 + 65 = 120 -> 55 + 78 = 133
    # Zone 2: 55 + 78 = 133 -> 55 + 91 = 146
    zones = calculate_heart_rate_zones(55, 185)

    assert "Zone 1 (Recovery)" in zones
    assert "Zone 2 (Aerobic/Easy)" in zones
    assert "Zone 3 (Tempo)" in zones
    assert "Zone 4 (Threshold)" in zones
    assert "Zone 5 (Anaerobic/Max)" in zones

    assert zones["Zone 2 (Aerobic/Easy)"] == "133 - 146 bpm"
