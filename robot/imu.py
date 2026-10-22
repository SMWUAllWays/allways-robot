
from dataclasses import dataclass
from enum import Enum
from math import atan2, degrees, hypot, tan, radians, isfinite


class SlopeStatus(str, Enum):
    PASSABLE = "통행 가능"
    STEEP = "경사 심함"
    UNKNOWN = "확인 필요"


@dataclass(frozen=True)
class SlopeResult:
    angle_deg: float | None
    slope_percent: float | None
    status: SlopeStatus
    reason: str


def calculate_slope(
    ax: float,
    ay: float,
    az: float,
) -> tuple[float, float]:
    """
    MPU6050 가속도 데이터로 경사도 계산.

    가정:
    - 센서 X축: 로봇 진행 방향
    - 센서 Z축: 평지에서 위쪽
    - 로봇은 측정 시 정지 상태
    """

    values = (ax, ay, az)

    if any(
        isinstance(v, bool)
        or not isinstance(v, (int, float))
        or not isfinite(v)
        for v in values
    ):
        raise ValueError("유효하지 않은 가속도 데이터입니다.")

    magnitude = hypot(ax, ay, az)

    if magnitude < 1e-6:
        raise ValueError("가속도 데이터가 유효하지 않습니다.")

    # 진행 방향의 경사각
    angle_deg = degrees(
        atan2(ax, hypot(ay, az))
    )

    # 경사율 (%) = tan(경사각) * 100
    slope_percent = tan(radians(angle_deg)) * 100

    return angle_deg, slope_percent


def evaluate_slope(
    ax: float,
    ay: float,
    az: float,
    max_slope_percent: float = 8.0,
) -> SlopeResult:

    if (
        isinstance(max_slope_percent, bool)
        or not isinstance(max_slope_percent, (int, float))
        or not isfinite(max_slope_percent)
        or max_slope_percent < 0
    ):
        raise ValueError("최대 허용 경사율이 유효하지 않습니다.")

    try:
        angle_deg, slope_percent = calculate_slope(
            ax, ay, az
        )
    except ValueError:
        return SlopeResult(
            None,
            None,
            SlopeStatus.UNKNOWN,
            "센서 데이터가 유효하지 않습니다.",
        )

    if abs(slope_percent) > max_slope_percent:
        return SlopeResult(
            angle_deg,
            slope_percent,
            SlopeStatus.STEEP,
            "설정한 최대 허용 경사율을 초과했습니다.",
        )

    return SlopeResult(
        angle_deg,
        slope_percent,
        SlopeStatus.PASSABLE,
        "설정한 최대 허용 경사율 이내입니다.",
    )


if __name__ == "__main__":
    result = evaluate_slope(
        ax=0.05,
        ay=0.0,
        az=1.0,
    )

    print(result)
