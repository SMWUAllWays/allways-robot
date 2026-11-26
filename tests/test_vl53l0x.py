from robot.vl53l0x import initialise_pair


class FakePin:
    def __init__(self, bus, side):
        self.bus = bus
        self.side = side
        self.value = None

    def switch_to_output(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, enabled):
        self._value = enabled
        if enabled:
            self.bus.enabled.add(self.side)
        else:
            self.bus.enabled.discard(self.side)


class FakeSensor:
    def set_address(self, address):
        assert address not in self.bus.addresses
        self.bus.addresses[address] = self.side
        self.address = address


class FakeBus:
    def __init__(self):
        self.enabled = set()
        self.addresses = {}


def make_sensor(bus):
    not_yet_addressed = bus.enabled - set(bus.addresses.values())
    assert len(not_yet_addressed) == 1
    sensor = FakeSensor()
    sensor.side = not_yet_addressed.pop()
    sensor.address = 0x29
    sensor.measurement_timing_budget = None
    sensor.bus = bus
    return sensor


def test_pair_initializes_one_at_a_time_with_unique_addresses():
    bus = FakeBus()
    left_pin = FakePin(bus, "left")
    right_pin = FakePin(bus, "right")

    sensors = initialise_pair(bus, [left_pin, right_pin], make_sensor, sleep=lambda _: None)

    assert [sensor.side for sensor in sensors] == ["left", "right"]
    assert [sensor.address for sensor in sensors] == [0x30, 0x31]
    assert [sensor.measurement_timing_budget for sensor in sensors] == [33000, 33000]
    assert bus.addresses == {0x30: "left", 0x31: "right"}
    assert left_pin.value is True
    assert right_pin.value is True
