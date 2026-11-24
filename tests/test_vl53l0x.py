from robot.vl53l0x import initialise_pair


class FakePin:
    def __init__(self, side):
        self.side = side
        self.value = None

    def switch_to_output(self, value):
        self.value = value


class FakeSensor:
    def set_address(self, address):
        assert address not in self.bus.addresses
        self.bus.addresses.add(address)
        self.address = address


class FakeBus:
    def __init__(self):
        self.active_sensor = None
        self.addresses = set()


def make_sensor(bus):
    assert bus.active_sensor is not None
    sensor = FakeSensor()
    sensor.side = bus.active_sensor
    sensor.address = 0x29
    sensor.measurement_timing_budget = None
    sensor.bus = bus
    return sensor


def test_pair_initializes_one_at_a_time_with_unique_addresses():
    bus = FakeBus()
    left_pin = FakePin("left")
    right_pin = FakePin("right")

    def sleep(_):
        active = [pin.side for pin in (left_pin, right_pin) if pin.value]
        assert len(active) <= 1
        bus.active_sensor = active[0] if active else None

    sensors = initialise_pair(bus, [left_pin, right_pin], make_sensor, sleep=sleep)

    assert [sensor.side for sensor in sensors] == ["left", "right"]
    assert [sensor.address for sensor in sensors] == [0x30, 0x31]
    assert [sensor.measurement_timing_budget for sensor in sensors] == [33000, 33000]
    assert left_pin.value is True
    assert right_pin.value is True
