
import pytest

from robot.motor import MotorController, MotorCommand


def test_initial_state():
    motor = MotorController()

    assert motor.current_command == MotorCommand(0, 0)


def test_forward():
    motor = MotorController()

    assert motor.forward(50) == MotorCommand(50, 50)


def test_backward():
    motor = MotorController()

    assert motor.backward(50) == MotorCommand(-50, -50)


def test_turn_left():
    motor = MotorController()

    assert motor.turn_left(30) == MotorCommand(-30, 30)


def test_turn_right():
    motor = MotorController()

    assert motor.turn_right(30) == MotorCommand(30, -30)


def test_stop():
    motor = MotorController()

    motor.forward(50)
    result = motor.stop()

    assert result == MotorCommand(0, 0)


def test_invalid_speed():
    motor = MotorController()

    with pytest.raises(ValueError):
        motor.forward(150)


def test_invalid_negative_speed():
    motor = MotorController()

    with pytest.raises(ValueError):
        motor.backward(-20)
