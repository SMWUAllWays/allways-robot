# 좌우 VL53L0X 연결·실행 안내

일반 Raspberry Pi의 Raspberry Pi OS / Python 3.10 이상 기준입니다(Pico용 아님).
이 프로그램은 거리 출력만 하며 모터를 작동시키지 않습니다.
실제 센서가 연결된 Pi에서 최종 확인해야 합니다.

## 1. 먼저 배선 확인

전원을 끈 뒤 센서 보드의 핀 글씨와 Pi의 실제 연결 핀을 확인하세요.
**선 색으로 역할을 판단하지 마세요.** 빨간 선도 전원선일 수 있습니다.
확인할 정보: Pi 모델, 센서 보드 앞뒤 사진, 좌우 각 선이 연결된 핀,
특히 추가 선의 센서 쪽 표기(XSHUT / SHDN / GPIO1 / VIN 등)와 Pi 쪽 핀 번호.
GPIO1은 XSHUT과 다른 핀이므로 이 코드의 제어선으로 사용할 수 없습니다.

아래는 배선 예시입니다. 기존 배선에 이미 모터 등이 연결돼 있다면 빈 GPIO를 골라야 합니다.

| 센서 연결 | Raspberry Pi 40핀 헤더 |
| --- | --- |
| 양쪽 SDA | GPIO2, 물리 3번 |
| 양쪽 SCL | GPIO3, 물리 5번 |
| 양쪽 GND | GND, 예: 물리 6번 |
| 양쪽 전원 | 보드 사양 확인 후 연결. 3.3V 입력을 지원하는 모듈이면 3.3V 물리 1번 사용 가능 |
| 오른쪽 XSHUT (현재 연결) | GPIO17, 물리 11번 |
| 왼쪽 XSHUT (추가 연결 필요) | GPIO27, 물리 13번 |

裸 센서 칩과 전압 조정기가 있는 모듈은 전원 조건이 다릅니다.
Pi의 GPIO/SDA/SCL에 5V를 연결하지 마세요. XSHUT 허용 전압과 모듈의 풀업도 확인하세요.
이 테스트 코드는 두 XSHUT을 각각 GPIO 출력으로 제어합니다.
모듈 전압 및 XSHUT 핀의 전기적 사양을 확인하기 전에는 실행하지 마세요.
GPIO에는 5V를 넣지 마세요. 확인 후 실행할 때만 `--confirm-xshut-safe`를 붙입니다.

두 센서의 초기 I2C 주소는 모두 0x29입니다. 이 스크립트는 두 XSHUT을 모두
개별 제어해서 한 대씩 켜고 0x30, 0x31 주소를 배정합니다.
현재 Pi에 오른쪽 센서 XSHUT만 GPIO17로 연결되어 있다면, 왼쪽 센서 XSHUT도
GPIO27에 연결해야 이 스크립트를 실행할 수 있습니다. 현재 한 개 XSHUT 배선은
이 스크립트의 배선 조건을 충족하지 않습니다. 주소는 전원을 껐다 켜면 0x29로 돌아옵니다.
센서는 초기화할 때마다 0x30, 0x31로 배정합니다. 전원을 끄면 원래 주소로 돌아갑니다.
다른 장치가 0x29/0x30/0x31을 사용하는 버스에서는 이 예제를 그대로 실행하지 마세요.

## 2. 컴퓨터에서 Pi에 접속

이미 쓰던 SD카드는 재설치하지 마세요. Pi에 모니터/키보드를 연결할 수 있다면
현재 OS에서 Wi-Fi를 연결하고 `sudo raspi-config`의 Interface Options → SSH를 켭니다.
로그인 계정을 알고 있어야 하며, 해당 계정의 비밀번호 변경은 Pi에서 `passwd`로 합니다.

새 SD카드를 준비하는 경우 Raspberry Pi Imager에서 Raspberry Pi OS를 선택하고
사용자 설정에 호스트명(예: `allways-pi`), 사용자명, 로그인 비밀번호,
Wi-Fi 이름(SSID)·Wi-Fi 비밀번호·국가(KR)를 지정합니다.
원격 접속 설정에서는 SSH와 비밀번호 인증을 활성화합니다.
로그인 비밀번호와 Wi-Fi 비밀번호는 서로 다른 용도이며 채팅에 공유할 필요가 없습니다.
기존 SD카드에 OS를 쓰면 내용이 지워집니다.

PC와 Pi를 같은 공유기에 연결하세요(PC는 유선이어도 됩니다).
게스트 Wi-Fi의 기기 간 통신 차단이 켜져 있으면 접속이 안 될 수 있습니다.
Windows PowerShell에서 아래의 `사용자명`을 실제 계정으로 바꿉니다.

```powershell
ssh 사용자명@allways-pi.local
```

처음 연결할 때 표시되는 장치가 본인 Pi인지 확인한 뒤 승인하고 로그인 비밀번호를 입력합니다.
비밀번호 입력 중 글자가 안 보이는 것은 정상입니다.
`.local`이 안 되면 Pi 터미널의 `hostname -I` 또는 공유기 연결 목록에서 IP를 찾고
`ssh 사용자명@192.168.x.x`처럼 실제 IP로 연결합니다.
일반적인 Raspberry Pi는 USB 케이블만 PC에 꽂는 것으로 SSH 연결되지 않습니다.
Pi에는 모델에 맞는 전원 공급이 필요합니다.

## 3. 현재 PC의 코드를 Pi로 복사

아직 GitHub로 올리지 않은 변경도 복사하려면 PC PowerShell에서 다음을 실행합니다.
주소와 사용자명은 실제 값으로 바꾸세요. 아래 복사는 Pi 홈에 프로젝트 폴더가 없다는 기준입니다.
이미 있다면 다른 폴더 이름을 사용해 기존 작업과 섞이지 않게 하세요.

```powershell
ssh 사용자명@allways-pi.local "mkdir -p ~/allways-sensor-test"
scp -r robot docs requirements-pi.txt 사용자명@allways-pi.local:~/allways-sensor-test/
```

PC에서는 이 저장소 폴더에서 실행합니다. 이후 명령은 **SSH로 접속한 Pi 안에서** 실행합니다.

```bash
sudo raspi-config
# Interface Options → I2C → Enable. 재부팅을 요청하면 재부팅 후 다시 SSH 접속
sudo apt update
sudo apt install -y python3-venv python3-dev i2c-tools
cd ~/allways-sensor-test
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-pi.txt
ls -l /dev/i2c-1
```

장치 접근 권한 오류가 나면 `groups`로 `i2c`, `gpio` 그룹을 확인합니다.
필요하다면 `sudo usermod -aG i2c,gpio "$USER"` 후 로그아웃하고 다시 접속합니다.

## 4. 배선에 맞게 실행

GPIO 번호는 **BCM 번호**입니다. 아래 17은 물리 17번 핀이 아닙니다.
반드시 확인된 배선에 맞게 숫자를 바꾸세요. `none`은 XSHUT이 미연결이고
보드 자체 풀업으로 센서가 항상 켜지는 쪽에만 사용합니다.

```bash
# 양쪽 XSHUT 연결: 오른쪽 GPIO17(기존), 왼쪽 GPIO27(추가)
python -m robot.vl53l0x --confirm-xshut-safe

# 10번 출력하고 종료
python -m robot.vl53l0x --count 10 --confirm-xshut-safe
```

`left=... mm  right=... mm`가 0.5초마다 출력됩니다. Ctrl+C로 종료합니다.
좌우 각각 앞에 물체를 옮겨 해당 값만 주로 변하는지 확인하세요.
센서가 서로 마주 보거나 시야가 겹치지 않게 두세요. 읽기는 순차로 진행합니다.
`None`은 기존 거리 검증 기준(30~2000mm)을 벗어난 값입니다.
통신 실패나 시간 초과면 중단하고 오류를 출력합니다. 오류를 0mm로 대체하지 않습니다.
테스트 중에는 이 프로그램 하나만 센서에 접근하게 하세요.

## 5. 인식이 안 될 때

전원을 끄고 한 개씩만 연결한 뒤 `i2cdetect -y 1`로 0x29가 보이는지 확인합니다.
두 개 연결 상태에서 0x29 하나만 보이는 것은 두 개가 정상 작동한다는 증거가 아닙니다.
배선·풀업·공통 GND·I2C 활성화·실제 XSHUT 핀·BCM/물리 번호 혼동을 확인하세요.
스크립트를 끝내면 양쪽 XSHUT을 LOW로 내려 센서를 종료합니다. 다시 실행하면
초기 주소 0x29부터 주소 배정을 다시 수행합니다.

## 참고 문서

- [Adafruit 드라이버와 주소 변경 예제](https://docs.circuitpython.org/projects/vl53l0x/en/latest/examples.html)
- [Pololu 모듈의 전원·XSHUT 사양](https://www.pololu.com/product/2490)
- [Raspberry Pi 설치·Wi-Fi·SSH 설정](https://www.raspberrypi.com/documentation/computers/getting-started.html)
- [Raspberry Pi 시스템 설정](https://www.raspberrypi.com/documentation/computers/configuration.html)
