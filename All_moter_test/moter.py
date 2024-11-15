from pynput import keyboard
import RPi.GPIO as GPIO
import time
from adafruit_pca9685 import PCA9685
import board 
import  busio

# PCA9685 서보모터 설정
i2c = busio.I2C(board.SCL, board.SDA)
pwm = PCA9685(i2c)
pwm.frequency = 50  # 서보모터 주파수 설정 (50Hz)
  
servo_channel = pwm.channels[0 ]  # 서보모터 채널 0 사용

# 서보모터 각도 설정 함수
def set_servo_angle(angle):
    # 각도를 PWM 신호로 변환
    min_pulse = 1638    # 0도에 해당하는 최소 펄스
    max_pulse = 8192    # 180도에 해당하는 최대 펄스
    pulse = int(min_pulse + (angle / 180.0) * (max_pulse - min_pulse))
    servo_channel.duty_cycle = pulse

# L298N DC 모터 설정
GPIO.setmode(GPIO.BCM)
IN1 = 17
IN2 = 27
ENA = 18

GPIO.setup(IN1, GPIO. OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

dc_motor_pwm = GPIO.PWM(ENA, 100)  # 속도 제어 PWM 설정
dc_motor_pwm.start(0)

# DC 모터 속도 및 제한 설정
current_speed = 0
MAX_SPEED = 100
MIN_SPEED = 0
SPEED_INCREMENT = 5  # 속도를 5씩 증가/감소

# DC 모터 전진 함수 (속도 증가)
def motor_forward():
    global current_speed
    if current_speed < MAX_SPEED:
        current_speed += SPEED_INCREMENT
    GPIO.output(IN1, GPIO.LOW) 
    GPIO.output(IN2, GPIO.HIGH)
    dc_motor_pwm.ChangeDutyCycle(current_speed)
    print(f"전진: 속도 {current_speed}%")

# DC 모터 속도 감소 함수
def motor_slow_down():
    global current_speed
    if current_speed > MIN_SPEED:
        current_speed -= SPEED_INCREMENT
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

# 초기 서보모터 각도 설정 (90도)
current_angle = 90
set_servo_angle(current_angle)

# 각도 변화량
ANGLE_INCREMENT = 5

# 키 입력 처리 함수
def on_press(key):
    global current_angle
    try:
        if key == keyboard.Key.up:  # 위쪽 방향키: DC 모터 전진 (속도 증가)
            motor_forward()
        elif key == keyboard.Key.down:  # 아래쪽 방향키: DC 모터 속도 감소
            motor_slow_down()
        elif key == keyboard.Key.left:  # 왼쪽 방향키: 서보모터 왼쪽 회전
            current_angle = max(0, current_angle - ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"서보모터 왼쪽 회전: 각도 {current_angle}도")
        elif key == keyboard.Key.right:  # 오른쪽 방향키: 서보모터 오른쪽 회전
            current_angle = min(180, current_angle + ANGLE_INCREMENT)
            set_servo_angle(current_angle)
            print(f"서보모터 오른쪽 회전: 각도 {current_angle}도")
        elif key == keyboard.Key.space:  # Space 키: 모터 정지
            motor_stop()
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        # ESC 키를 누르면 프로그램 종료
        print("프로그램을 종료합니다.")
        return False

# 키보드 리스너 시작
print("키 입력을 기다리는 중입니다...")
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# 메인 루프
try:
    listener.join()  # 키보드 리스너가 종료될 때까지 대기
except KeyboardInterrupt:
    GPIO.cleanup()  # 프로그램 종료 시 GPIO 핀 초기화
    print("프로그램을 종료합니다.")
