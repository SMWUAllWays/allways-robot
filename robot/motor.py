
from dataclasses import dataclass


@dataclass(frozen=True)
class MotorCommand:
    left_speed: float
    right_speed: float


class MotorController:
    """
    차동 구동 방식의 좌우 모터 명령 생성기.

    속도 범위: -100 ~ 100
    양수: 전진
    음수: 후진
    0: 정지

    실제 GPIO 출력은 아직 구현하지 않음.
    """

    def __init__(self):
        self.current_command = MotorCommand(0, 0)

    def set_speed(
        self,
        left_speed: float,
        right_speed: float,
    ) -> MotorCommand:

        for speed in (left_speed, right_speed):
            if isinstance(speed, bool) or not isinstance(
                speed, (int, float)
            ):
                raise ValueError("속도는 숫자여야 합니다.")

            if not -100 <= speed <= 100:
                raise ValueError("속도는 -100~100 범위여야 합니다.")

        self.current_command = MotorCommand(
            left_speed=left_speed,
            right_speed=right_speed,
        )

        return self.current_command

    def forward(self, speed: float = 50) -> MotorCommand:
        self._validate_direction_speed(speed)
        return self.set_speed(speed, speed)

    def backward(self, speed: float = 50) -> MotorCommand:
        self._validate_direction_speed(speed)
        return self.set_speed(-speed, -speed)

    def turn_left(self, speed: float = 50) -> MotorCommand:
        self._validate_direction_speed(speed)
        return self.set_speed(-speed, speed)

    def turn_right(self, speed: float = 50) -> MotorCommand:
        self._validate_direction_speed(speed)
        return self.set_speed(speed, -speed)

    def stop(self) -> MotorCommand:
        return self.set_speed(0, 0)

    @staticmethod
    def _validate_direction_speed(speed: float) -> None:
        if (
            isinstance(speed, bool)
            or not isinstance(speed, (int, float))
            or not 0 <= speed <= 100
        ):
            raise ValueError("방향별 속도는 0~100 범위여야 합니다.")


if __name__ == "__main__":
    motor = MotorController()

    print("전진:", motor.forward(50))
    print("좌회전:", motor.turn_left(30))
    print("우회전:", motor.turn_right(30))
    print("정지:", motor.stop())
