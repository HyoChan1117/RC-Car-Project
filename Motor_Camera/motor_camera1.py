import time
import os
import subprocess
import threading
import csv
from pynput import keyboard
import RPi.GPIO as GPIO

# GPIO 핀 설정
SERVO_PIN = 12  # 서보모터 핀 번호
IN1 = 17        # DC 모터 IN1 핀 번호
IN2 = 27        # DC 모터 IN2 핀 번호
ENA = 18        # DC 모터 ENA 핀 번호

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# PWM 설정
servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 서보모터: 50Hz
dc_motor_pwm = GPIO.PWM(ENA, 100)    # DC 모터: 100Hz

# PWM 시작
servo_pwm.start(0)
dc_motor_pwm.start(0)

# 초기값 설정
current_angle = 90
current_speed = 0

# 서보모터 각도 설정 함수
def set_servo_angle(angle):
    # 각도를 듀티 사이클로 변환 (0도 = 2%, 180도 = 12%)
    duty = 2 + (angle / 18)
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.1)
    servo_pwm.ChangeDutyCycle(0)  # 과열 방지

# DC 모터 전진 함수 (속도 증가)
def motor_forward():
    global current_speed
    if current_speed < 100:
        current_speed += 5
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"전진: 속도 {current_speed}%")

# DC 모터 속도 감소 함수
def motor_slow_down():
    global current_speed
    if current_speed > 0:
        current_speed -= 5
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"속도 감소: 속도 {current_speed}%")

# 모터 정지 함수
def motor_stop():
    global current_speed
    current_speed = 0
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    dc_motor_pwm.ChangeDutyCycle(0)
    print("모터 정지")

# 사진 촬영 및 CSV 저장
def capture_image_with_label(label):
    session_dir = "dataset/session_01"
    os.makedirs(session_dir, exist_ok=True)
    csv_path = "dataset/line_tracking_data.csv"

    # CSV 파일 초기화 (최초 실행 시 열 생성)
    if not os.path.exists(csv_path):
        with open(csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["image_path", "timestamp", "label"])

    # 사진 촬영 및 저장
    timestamp = int(time.time() * 1000)
    file_path = f"{session_dir}/image_{label}_{timestamp}.jpg"
    try:
        subprocess.run(["libcamera-still", "-o", file_path, "--nopreview"], check=True)
        print(f"사진 촬영 완료: {file_path}")

        # CSV에 저장
        with open(csv_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([file_path, timestamp, label])
            print(f"데이터 저장 완료: {file_path}, {label}")

        # 리소스 해제 및 안정화 대기
        subprocess.run(["killall", "libcamera-still"], check=False)
        time.sleep(0.5)  # 카메라 안정화를 위해 대기
    except subprocess.CalledProcessError:
        print(f"사진 촬영 실패: {file_path}")

# 초기 서보모터 각도 설정
set_servo_angle(current_angle)

ANGLE_INCREMENT = 5

# 라벨 입력 변수
current_label = "none"

# 키 입력 처리
def on_press(key):
    global current_angle, current_label
    try:
        if key == keyboard.Key.up:
            motor_forward()
        elif key == keyboard.Key.down:
            motor_slow_down()
        elif key == keyboard.Key.left:
            current_angle = max(0, current_angle - ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"서보모터 왼쪽 회전: 각도 {current_angle}도")
        elif key == keyboard.Key.right:
            current_angle = min(180, current_angle + ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"서보모터 오른쪽 회전: 각도 {current_angle}도")
        elif key == keyboard.Key.space:
            motor_stop()
        elif hasattr(key, 'char') and key.char in ['s', 'l', 'r']:
            current_label = {'s': 'straight', 'l': 'left_turn', 'r': 'right_turn'}[key.char]
            print(f"라벨 변경: {current_label}")
            capture_image_with_label(current_label)  # 기본 촬영(1장)
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        print("프로그램을 종료합니다.")
        return False

# 키보드 리스너 스레드
def motor_control_thread():
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    listener.join()

# 메인 실행
try:
    motor_thread = threading.Thread(target=motor_control_thread)
    motor_thread.start()
    motor_thread.join()
except KeyboardInterrupt:
    print("프로그램 종료 중...")
finally:
    servo_pwm.stop()
    dc_motor_pwm.stop()
    GPIO.cleanup()
    print("프로그램이 종료되었습니다.")
