
from dataclasses import dataclass
from enum import Enum
from math import isfinite


class PassageStatus(str, Enum):
    PASSABLE = "통행 가능"
    BLOCKED = "통행 불가"
    CAUTION = "주의"
    UNKNOWN = "확인 필요"


@dataclass
class WidthResult:
    left_distance_mm: float | None
    right_distance_mm: float | None
    width_mm: float | None
    status: PassageStatus
    reason: str


def is_valid_distance(
    distance_mm: float | None,
    min_range_mm: float = 30,
    max_range_mm: float = 2000,
) -> bool:
    """거리센서 측정값의 유효성을 확인한다."""

    if distance_mm is None:
        return False

    if isinstance(distance_mm, bool):
        return False

    if not isinstance(distance_mm, (int, float)):
        return False

    if not isfinite(distance_mm):
        return False

    return min_range_mm <= distance_mm <= max_range_mm


def calculate_width(
    left_mm: float | None,
    right_mm: float | None,
    baseline_mm: float,
) -> float | None:
    """
    통로 폭을 계산한다.

    가정:
    - 좌우 센서가 각각 벽을 향해 수직으로 설치됨
    - baseline_mm은 두 센서의 측정 기준점 사이 거리
    - 단위는 모두 mm
    """

    if not is_valid_distance(left_mm):
        return None

    if not is_valid_distance(right_mm):
        return None

    if not isfinite(baseline_mm) or baseline_mm <= 0:
        raise ValueError("센서 간 기준 거리는 0보다 커야 합니다.")

    return left_mm + right_mm + baseline_mm


def evaluate_passage(
    left_mm: float | None,
    right_mm: float | None,
    baseline_mm: float,
    required_width_mm: float,
    safety_margin_mm: float = 50,
) -> WidthResult:
    """
    측정한 통로 폭을 사용자 최소 통행 폭과 비교한다.

    PASSABLE: 최소 폭 + 안전 여유 폭 이상
    CAUTION: 최소 폭 이상이지만 안전 여유 폭 미달
    BLOCKED: 최소 폭 미달
    UNKNOWN: 센서 측정값이 유효하지 않음
    """

    if not isfinite(required_width_mm) or required_width_mm <= 0:
        raise ValueError("최소 통행 폭은 0보다 커야 합니다.")

    if not isfinite(safety_margin_mm) or safety_margin_mm < 0:
        raise ValueError("안전 여유 폭은 0 이상이어야 합니다.")

    width_mm = calculate_width(
        left_mm,
        right_mm,
        baseline_mm,
    )

    if width_mm is None:
        return WidthResult(
            left_distance_mm=left_mm,
            right_distance_mm=right_mm,
            width_mm=None,
            status=PassageStatus.UNKNOWN,
            reason="센서 측정값이 유효하지 않아 확인이 필요합니다.",
        )

    if width_mm < required_width_mm:
        status = PassageStatus.BLOCKED
        reason = "사용자에게 필요한 최소 통행 폭보다 좁습니다."

    elif width_mm < required_width_mm + safety_margin_mm:
        status = PassageStatus.CAUTION
        reason = "최소 통행 폭은 충족하지만 안전 여유가 부족합니다."

    else:
        status = PassageStatus.PASSABLE
        reason = "설정한 최소 통행 폭과 안전 여유를 충족합니다."

    return WidthResult(
        left_distance_mm=left_mm,
        right_distance_mm=right_mm,
        width_mm=width_mm,
        status=status,
        reason=reason,
    )


if __name__ == "__main__":
    result = evaluate_passage(
        left_mm=500,
        right_mm=600,
        baseline_mm=100,
        required_width_mm=900,
    )

    print(f"왼쪽 거리: {result.left_distance_mm} mm")
    print(f"오른쪽 거리: {result.right_distance_mm} mm")
    print(f"통로 폭: {result.width_mm} mm")
    print(f"통행 판정: {result.status.value}")
    print(f"판정 이유: {result.reason}")
