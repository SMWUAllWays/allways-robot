
import pytest

from robot.imu import (
    SlopeStatus,
    calculate_slope,
    evaluate_slope,
)


def test_flat_surface():
    angle, slope = calculate_slope(0, 0, 1)

    assert angle == pytest.approx(0)
    assert slope == pytest.approx(0)


def test_positive_slope():
    angle, slope = calculate_slope(0.1, 0, 1)

    assert angle > 0
    assert slope == pytest.approx(10.0)


def test_negative_slope():
    angle, slope = calculate_slope(-0.1, 0, 1)

    assert angle < 0
    assert slope == pytest.approx(-10.0)


def test_passable_slope():
    result = evaluate_slope(0.05, 0, 1)

    assert result.status == SlopeStatus.PASSABLE


def test_steep_slope():
    result = evaluate_slope(0.15, 0, 1)

    assert result.status == SlopeStatus.STEEP


def test_invalid_acceleration():
    result = evaluate_slope(0, 0, 0)

    assert result.status == SlopeStatus.UNKNOWN
    assert result.slope_percent is None


def test_invalid_threshold():
    with pytest.raises(ValueError):
        evaluate_slope(0, 0, 1, max_slope_percent=-1)


def test_invalid_nan():
    result = evaluate_slope(float("nan"), 0, 1)

    assert result.status == SlopeStatus.UNKNOWN
