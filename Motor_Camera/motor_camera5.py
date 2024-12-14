import RPi.GPIO as GPIO
import time
import threading
import cv2
import os
import sys
import termios
import tty

# 핀 설정
DC_MOTOR = {"IN1": 17, "IN2": 27, "ENA": 18}  # DC 모터 핀
SERVO_PIN = 12  # 서보 모터 핀

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setup(list(DC_MOTOR.values()), GPIO.OUT)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# PWM 초기화
pwm_dc = GPIO.PWM(DC_MOTOR["ENA"], 1000)  # DC 모터 PWM
pwm_servo = GPIO.PWM(SERVO_PIN, 50)       # 서보 모터 PWM
pwm_dc.start(0)
pwm_servo.start(0)

# 카메라 초기화
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("에러: 카메라를 열 수 없습니다.")
    sys.exit()

# 키보드 입력 처리 함수
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# 모터 제어
def control_motor(direction, speed=0):
    states = {
        "forward": (GPIO.HIGH, GPIO.LOW),
        "backward": (GPIO.LOW, GPIO.HIGH),
        "stop": (GPIO.LOW, GPIO.LOW),
    }
    GPIO.output(DC_MOTOR["IN1"], states[direction][0])
    GPIO.output(DC_MOTOR["IN2"], states[direction][1])
    pwm_dc.ChangeDutyCycle(speed)

# 서보 모터 제어
def control_servo(angle):
    pwm_servo.ChangeDutyCycle(2.5 + angle / 18)

# 이미지 캡처
def capture_images(folder="/home/pi/Desktop/captured_images"):
    os.makedirs(folder, exist_ok=True)
    while capturing:
        ret, frame = cap.read()
        if ret:
            filename = os.path.join(folder, f"image_{time.strftime('%Y%m%d_%H%M%S')}.jpg")
            cv2.imwrite(filename, frame)
        time.sleep(0.5)

# 메인 루프
try:
    print("W: 앞으로, S: 뒤로, 스페이스바: 정지, A: 서보 왼쪽, D: 서보 오른쪽")
    print("+: 속도 증가, -: 속도 감소, E: 서보 중앙, Q: 종료")

    speed, angle = 30, 55  # 초기값
    capturing = True
    threading.Thread(target=capture_images, daemon=True).start()

    while True:
        key = get_key()

        if key == 'w':  # 앞으로
            control_motor("forward", speed)
        elif key == 's':  # 뒤로
            control_motor("backward", speed)
        elif key == ' ':  # 스페이스바: 정지
            control_motor("stop")
        elif key == '+':  # 속도 증가
            speed = min(100, speed + 5)
        elif key == '-':  # 속도 감소
            speed = max(0, speed - 5)
        elif key == 'a':  # 서보 왼쪽
            angle = max(30, angle - 15)
            control_servo(angle)
        elif key == 'd':  # 서보 오른쪽
            angle = min(80, angle + 15)
            control_servo(angle)
        elif key == 'e':  # 서보 중앙
            angle = 55
            control_servo(angle)
        elif key == 'q':  # 종료
            break

finally:
    capturing = False
    control_motor("stop")
    pwm_dc.stop()
    pwm_servo.stop()
    GPIO.cleanup()
    cap.release()
    cv2.destroyAllWindows()
    print("프로그램 종료")
