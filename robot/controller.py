
from dataclasses import dataclass

from robot.distance import DistanceSensorManager
from robot.width import evaluate_passage, WidthResult
from robot.safety import check_obstacle, SafetyResult
from robot.imu import evaluate_slope, SlopeResult
from robot.motor import MotorController, MotorCommand


@dataclass(frozen=True)
class RobotState:
    safety: SafetyResult
    width: WidthResult
    slope: SlopeResult
    motor: MotorCommand


class RobotController:
    def __init__(
        self,
        distance_sensors: DistanceSensorManager,
        motor: MotorController,
        baseline_mm: float = 100,
        required_width_mm: float = 900,
        max_slope_percent: float = 8.0,
        stop_distance_mm: float = 300,
    ):
        self.distance_sensors = distance_sensors
        self.motor = motor
        self.baseline_mm = baseline_mm
        self.required_width_mm = required_width_mm
        self.max_slope_percent = max_slope_percent
        self.stop_distance_mm = stop_distance_mm

    def update(
        self,
        ax: float,
        ay: float,
        az: float,
        speed: float = 40,
    ) -> RobotState:
        """
        센서 측정 → 안전 판단 → 모터 명령 생성.

        실제 GPIO 출력 및 자율주행 조향은 아직 미구현.
        """

        # 1. 거리센서 데이터 수집
        distances = self.distance_sensors.read_all()

        # 2. 전방 장애물 확인
        safety = check_obstacle(
            distances.front_mm,
            self.stop_distance_mm,
        )

        # 3. 통로 폭 평가
        width = evaluate_passage(
            distances.left_mm,
            distances.right_mm,
            self.baseline_mm,
            self.required_width_mm,
        )

        # 4. 경사도 평가
        slope = evaluate_slope(
            ax,
            ay,
            az,
            self.max_slope_percent,
        )

        # 5. 안전 상태에 따라 모터 명령 생성
        if safety.should_stop:
            command = self.motor.stop()
        else:
            command = self.motor.forward(speed)

        return RobotState(
            safety=safety,
            width=width,
            slope=slope,
            motor=command,
        )
