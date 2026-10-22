
from robot.controller import RobotController
from robot.distance import DistanceSensorManager
from robot.motor import MotorController, MotorCommand
from robot.safety import SafetyStatus
from robot.width import PassageStatus
from robot.imu import SlopeStatus


def make_controller(left=500, right=600, front=800):
    sensors = DistanceSensorManager(
        read_left=lambda: left,
        read_right=lambda: right,
        read_front=lambda: front,
    )

    return RobotController(
        distance_sensors=sensors,
        motor=MotorController(),
    )


def test_safe_forward():
    controller = make_controller()

    state = controller.update(0, 0, 1)

    assert state.safety.status == SafetyStatus.CLEAR
    assert state.motor == MotorCommand(40, 40)


def test_obstacle_stop():
    controller = make_controller(front=200)

    state = controller.update(0, 0, 1)

    assert state.safety.status == SafetyStatus.STOP
    assert state.motor == MotorCommand(0, 0)


def test_sensor_error_stop():
    controller = make_controller(front=None)

    state = controller.update(0, 0, 1)

    assert state.safety.status == SafetyStatus.SENSOR_ERROR
    assert state.motor == MotorCommand(0, 0)


def test_width_evaluation():
    controller = make_controller(left=500, right=600)

    state = controller.update(0, 0, 1)

    assert state.width.status == PassageStatus.PASSABLE
    assert state.width.width_mm == 1200


def test_slope_evaluation():
    controller = make_controller()

    state = controller.update(0.15, 0, 1)

    assert state.slope.status == SlopeStatus.STEEP
    assert state.motor == MotorCommand(40, 40)
