# Unit test for get_running_weather_forecast tool

from app.agent import get_running_weather_forecast


def test_get_running_weather_forecast():
    # NYC Coordinates
    data = get_running_weather_forecast(40.7128, -74.0060)

    assert "temperature_celsius" in data
    assert "feels_like_celsius" in data
    assert "humidity_percent" in data
    assert "wind_speed_kmh" in data
    assert "summary" in data
