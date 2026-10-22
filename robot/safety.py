
from dataclasses import dataclass
from enum import Enum
from math import isfinite


class SafetyStatus(str, Enum):
    CLEAR = "주행 가능"
    STOP = "정지"
    SENSOR_ERROR = "센서 오류"


@dataclass
class SafetyResult:
    front_distance_mm: float | None
    status: SafetyStatus
    should_stop: bool
    reason: str


def check_obstacle(
    front_distance_mm: float | None,
    stop_distance_mm: float = 300,
) -> SafetyResult:
    """전방 장애물 거리로 정지 여부를 판단한다."""

    if not isfinite(stop_distance_mm) or stop_distance_mm <= 0:
        raise ValueError("정지 기준 거리는 0보다 커야 합니다.")

    # 측정 실패 시 안전을 위해 정지
    if (
        front_distance_mm is None
        or isinstance(front_distance_mm, bool)
        or not isinstance(front_distance_mm, (int, float))
        or not isfinite(front_distance_mm)
        or front_distance_mm <= 0
    ):
        return SafetyResult(
            front_distance_mm=front_distance_mm,
            status=SafetyStatus.SENSOR_ERROR,
            should_stop=True,
            reason="전방 거리 측정값이 유효하지 않아 정지합니다.",
        )

    if front_distance_mm <= stop_distance_mm:
        return SafetyResult(
            front_distance_mm=front_distance_mm,
            status=SafetyStatus.STOP,
            should_stop=True,
            reason="전방 장애물이 정지 기준 거리 이내에 있습니다.",
        )

    return SafetyResult(
        front_distance_mm=front_distance_mm,
        status=SafetyStatus.CLEAR,
        should_stop=False,
        reason="전방 장애물이 정지 기준 거리보다 멀리 있습니다.",
    )
