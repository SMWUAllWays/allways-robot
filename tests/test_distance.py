
from robot.distance import (
    DistanceReading,
    DistanceSensorManager,
    validate_distance,
)


def test_valid_distance():
    assert validate_distance(500) == 500.0


def test_invalid_distance():
    assert validate_distance(None) is None
    assert validate_distance(-10) is None
    assert validate_distance(3000) is None
    assert validate_distance(float("nan")) is None


def test_read_all():
    sensors = DistanceSensorManager(
        read_left=lambda: 500,
        read_right=lambda: 600,
        read_front=lambda: 800,
    )

    result = sensors.read_all()

    assert result == DistanceReading(
        left_mm=500.0,
        right_mm=600.0,
        front_mm=800.0,
    )


def test_sensor_invalid_reading():
    sensors = DistanceSensorManager(
        read_left=lambda: None,
        read_right=lambda: 600,
        read_front=lambda: 800,
    )

    result = sensors.read_all()

    assert result.left_mm is None
    assert result.right_mm == 600.0


def test_front_sensor_out_of_range():
    sensors = DistanceSensorManager(
        read_left=lambda: 500,
        read_right=lambda: 600,
        read_front=lambda: 2500,
    )

    result = sensors.read_all()

    assert result.front_mm is None
