# allways-robot
파이썬으로 배우는 머신러닝 로봇 코드

## Raspberry Pi 좌우 거리센서 테스트

[VL53L0X 두 개 배선, Wi-Fi/SSH 접속, 설치와 실행 안내](docs/vl53l0x.md)

오른쪽 XSHUT은 GPIO17, 왼쪽 XSHUT은 GPIO27에 연결하고 모듈의 XSHUT 전기 사양을 확인한 뒤 Pi에서 실행합니다.

```bash
python -m robot.vl53l0x --confirm-xshut-safe
```
