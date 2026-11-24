"""Read two VL53L0X sensors using separate XSHUT GPIOs on Raspberry Pi."""

import argparse
from contextlib import ExitStack
import time


def initialise_pair(i2c, pins, make_sensor, sleep=time.sleep):
    """Hold both sensors in reset, then assign unique addresses one by one."""
    if len(pins) != 2 or pins[0] is pins[1]:
        raise ValueError("Two separate XSHUT pins are required")

    sensors = []
    for pin in pins:
        pin.switch_to_output(value=False)
    sleep(0.1)

    try:
        for pin, address in zip(pins, (0x30, 0x31)):
            pin.value = True
            sleep(0.1)
            sensor = make_sensor(i2c)
            sensor.set_address(address)
            sensor.measurement_timing_budget = 33000
            sensors.append(sensor)
        return sensors
    except Exception:
        for pin in pins:
            pin.value = False
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=0, help="number of reads; 0 runs until Ctrl+C")
    parser.add_argument("--interval", type=float, default=0.2)
    parser.add_argument(
        "--confirm-xshut-safe",
        action="store_true",
        help="confirm the module's XSHUT voltage/pull-up is verified safe for direct Pi GPIO control",
    )
    args = parser.parse_args()
    if args.count < 0 or args.interval <= 0:
        parser.error("count must be >= 0 and interval must be > 0")
    if not args.confirm_xshut_safe:
        parser.error(
            "XSHUT electrical safety is unverified. Confirm the module pull-up/voltage first, "
            "then rerun with --confirm-xshut-safe."
        )

    # Import hardware-specific packages only on the Pi.
    import board
    import busio
    from digitalio import DigitalInOut
    import adafruit_vl53l0x

    # Existing robot wiring has the right sensor on GPIO17; add the left
    # sensor's XSHUT to GPIO27. Addresses then match these side labels.
    right_pin = DigitalInOut(board.D17)
    left_pin = DigitalInOut(board.D27)
    pins = [left_pin, right_pin]
    with ExitStack() as stack:
        for pin in pins:
            stack.callback(pin.deinit)
        i2c = busio.I2C(board.SCL, board.SDA)
        stack.callback(i2c.deinit)
        try:
            left, right = initialise_pair(i2c, pins, adafruit_vl53l0x.VL53L0X)
            print("주소 설정 완료: 왼쪽=0x30(GPIO27), 오른쪽=0x31(GPIO17)", flush=True)
            index = 0
            while args.count == 0 or index < args.count:
                print(f"left={left.range} mm  right={right.range} mm", flush=True)
                index += 1
                if args.count == 0 or index < args.count:
                    time.sleep(args.interval)
        finally:
            # Active-low XSHUT: stop both sensors before releasing the GPIOs.
            for pin in pins:
                try:
                    pin.value = False
                except (OSError, RuntimeError):
                    pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n센서 테스트 종료")
    except (OSError, RuntimeError, ValueError) as exc:
        raise SystemExit(f"센서 초기화/통신 실패: {exc}") from exc
