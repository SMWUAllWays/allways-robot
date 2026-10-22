
from dataclasses import dataclass
from math import isfinite
from typing import Callable


@dataclass(frozen=True)
class DistanceReading:
    left_mm: float | None
    right_mm: float | None
    front_mm: float | None


def validate_distance(
    value: float | None,
    min_mm: float = 30,
    max_mm: float = 2000,
) -> float | None:
    """측정값이 유효하면 반환하고, 아니면 None을 반환한다."""

    if value is None or isinstance(value, bool):
        return None

    if not isinstance(value, (int, float)):
        return None

    if not isfinite(value):
        return None

    if not min_mm <= value <= max_mm:
        return None

    return float(value)


class DistanceSensorManager:
    """
    좌측·우측·전방 거리센서의 측정값을 수집한다.

    각 센서의 측정 함수(read_left 등)를 주입받으므로
    실제 센서 연결 전에도 가상 데이터로 테스트할 수 있다.
    """

    def __init__(
        self,
        read_left: Callable[[], float | None],
        read_right: Callable[[], float | None],
        read_front: Callable[[], float | None],
    ):
        self.read_left = read_left
        self.read_right = read_right
        self.read_front = read_front

    def read_all(self) -> DistanceReading:
        return DistanceReading(
            left_mm=validate_distance(self.read_left()),
            right_mm=validate_distance(self.read_right()),
            front_mm=validate_distance(self.read_front()),
        )


if __name__ == "__main__":
    # 실제 센서 대신 가상 측정값 사용
    sensors = DistanceSensorManager(
        read_left=lambda: 500,
        read_right=lambda: 600,
        read_front=lambda: 800,
    )

    result = sensors.read_all()

    print(f"왼쪽 거리: {result.left_mm} mm")
    print(f"오른쪽 거리: {result.right_mm} mm")
    print(f"전방 거리: {result.front_mm} mm")
