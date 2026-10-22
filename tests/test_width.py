
import pytest

from robot.width import (
    PassageStatus,
    calculate_width,
    evaluate_passage,
    is_valid_distance,
)


def test_calculate_width():
    """정상적인 통로 폭 계산"""
    width = calculate_width(500, 600, 100)

    assert width == 1200


def test_passable():
    """충분히 넓은 통로"""
    result = evaluate_passage(
        left_mm=500,
        right_mm=600,
        baseline_mm=100,
        required_width_mm=900,
    )

    assert result.width_mm == 1200
    assert result.status == PassageStatus.PASSABLE


def test_blocked():
    """최소 통행 폭보다 좁은 통로"""
    result = evaluate_passage(
        left_mm=300,
        right_mm=350,
        baseline_mm=100,
        required_width_mm=900,
    )

    assert result.width_mm == 750
    assert result.status == PassageStatus.BLOCKED


def test_caution():
    """최소 폭은 충족하지만 안전 여유가 부족한 통로"""
    result = evaluate_passage(
        left_mm=400,
        right_mm=420,
        baseline_mm=100,
        required_width_mm=900,
        safety_margin_mm=50,
    )

    assert result.width_mm == 920
    assert result.status == PassageStatus.CAUTION


def test_invalid_sensor_value():
    """센서 측정 실패"""
    result = evaluate_passage(
        left_mm=None,
        right_mm=600,
        baseline_mm=100,
        required_width_mm=900,
    )

    assert result.width_mm is None
    assert result.status == PassageStatus.UNKNOWN


def test_out_of_range():
    """센서 범위를 벗어난 값"""
    assert is_valid_distance(3000) is False
    assert is_valid_distance(-10) is False
    assert is_valid_distance(float("nan")) is False


def test_invalid_baseline():
    """잘못된 센서 간 기준 거리"""
    with pytest.raises(ValueError):
        calculate_width(500, 600, 0)


def test_invalid_required_width():
    """잘못된 사용자 최소 통행 폭"""
    with pytest.raises(ValueError):
        evaluate_passage(500, 600, 100, -1)
