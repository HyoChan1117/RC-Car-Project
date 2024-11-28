import RPi.GPIO as GPIO
import time
from pynput import keyboard

# GPIO 핀 설정
SERVO_PIN = 12  # 서보모터가 연결된 GPIO 핀 번호
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# PWM 설정
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz 주파수로 PWM 시작
pwm.start(0)

# 서보모터 각도 설정 함수
def set_servo_angle(angle):
    # 각도를 PWM 듀티 사이클로 변환
    duty = 2 + (angle / 18)  # 0도 = 2%, 180도 = 12%
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.1)  # 서보모터가 움직일 시간을 줌
    pwm.ChangeDutyCycle(0)  # 신호를 끊어 서보모터 과열 방지

# 초기 각도 설정 (90도)
current_angle = 90
set_servo_angle(current_angle)

# 각도 변화량 설정
ANGLE_INCREMENT = 5

# 키보드 입력 처리 함수
def on_press(key):
    global current_angle
    try:
        if key == keyboard.Key.left:
            # 왼쪽 방향키를 눌렀을 때 각도 감소
            current_angle = max(0, current_angle - ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"왼쪽: 각도 {current_angle}도")
        elif key == keyboard.Key.right:
            # 오른쪽 방향키를 눌렀을 때 각도 증가
            current_angle = min(180, current_angle + ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"오른쪽: 각도 {current_angle}도")
    except AttributeError:
        pass

# 키보드 리스너 시작
listener = keyboard.Listener(on_press=on_press)
listener.start()

# 메인 루프
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    # 프로그램 종료 시 GPIO 정리
    pwm.stop()
    GPIO.cleanup()