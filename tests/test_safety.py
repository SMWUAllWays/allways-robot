
import pytest

from robot.safety import SafetyStatus, check_obstacle


def test_clear_path():
    result = check_obstacle(600)

    assert result.status == SafetyStatus.CLEAR
    assert result.should_stop is False


def test_obstacle_detected():
    result = check_obstacle(200)

    assert result.status == SafetyStatus.STOP
    assert result.should_stop is True


def test_stop_at_boundary():
    result = check_obstacle(300)

    assert result.status == SafetyStatus.STOP
    assert result.should_stop is True


def test_sensor_failure():
    result = check_obstacle(None)

    assert result.status == SafetyStatus.SENSOR_ERROR
    assert result.should_stop is True


def test_invalid_distance():
    result = check_obstacle(float("nan"))

    assert result.should_stop is True


def test_invalid_threshold():
    with pytest.raises(ValueError):
        check_obstacle(500, stop_distance_mm=0)
