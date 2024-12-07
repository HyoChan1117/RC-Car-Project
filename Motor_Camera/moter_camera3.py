import RPi.GPIO as GPIO
import time
import threading
import cv2
import os
import sys
import termios
import tty

# DC 모터 핀 설정
DC_MOTOR_IN1 = 17    # DC 모터 방향 1 (IN1) 핀
DC_MOTOR_IN2 = 27    # DC 모터 방향 2 (IN2) 핀
DC_MOTOR_ENA = 18    # DC 모터 속도 제어 (ENA, PWM 제어) 핀

# 서보 모터 핀 설정
SERVO_PIN = 12  # 서보 모터 PWM 신호 핀

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(DC_MOTOR_IN1, GPIO.OUT)
GPIO.setup(DC_MOTOR_IN2, GPIO.OUT)
GPIO.setup(DC_MOTOR_ENA, GPIO.OUT)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# DC 모터와 서보 모터의 PWM 초기화
pwm_dc = GPIO.PWM(DC_MOTOR_ENA, 1000)  # 주파수: 1kHz
pwm_servo = GPIO.PWM(SERVO_PIN, 50)  # 주파수: 50Hz (서보용)
pwm_dc.start(0)  # 0% 듀티 사이클로 시작 (모터 꺼짐)
pwm_servo.start(0)  # 서보 모터 초기 위치

# OpenCV 카메라 초기화
cap = cv2.VideoCapture(0)  # 기본 카메라 사용 (일반적으로 0)
if not cap.isOpened():
    print("에러: 카메라를 열 수 없습니다.")
    sys.exit()
else:
    print("카메라가 성공적으로 열렸습니다.")

# 키보드 입력 읽는 헬퍼 함수
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# DC 모터 방향과 속도 제어 함수
def dc_motor_control(direction, speed):
    if direction == "forward":
        GPIO.output(DC_MOTOR_IN1, GPIO.HIGH)
        GPIO.output(DC_MOTOR_IN2, GPIO.LOW)
        print("모터가 앞으로 이동합니다.")
    elif direction == "backward":
        GPIO.output(DC_MOTOR_IN1, GPIO.LOW)
        GPIO.output(DC_MOTOR_IN2, GPIO.HIGH)
        print("모터가 뒤로 이동합니다.")
    elif direction == "stop":
        GPIO.output(DC_MOTOR_IN1, GPIO.LOW)
        GPIO.output(DC_MOTOR_IN2, GPIO.LOW)
        print("모터가 정지했습니다.")
   
    # PWM으로 모터 속도 설정 (듀티 사이클 사용)
    pwm_dc.ChangeDutyCycle(speed)  # 속도: 듀티 사이클 (0-100)

# 서보 모터 제어 함수
def servo_control(angle):
    # 각도 (30-80도)를 PWM 듀티 사이클로 변환
    duty_cycle = 2.5 + (angle / 18)  # 서보 각도를 듀티 사이클 (2.5-12.5)로 변환
    pwm_servo.ChangeDutyCycle(duty_cycle)
    print(f"서보가 {angle}도로 이동했습니다.")

# 이미지를 계속 캡처하고 저장하는 함수
def capture_images():
    desktop_path = "/home/pi/Desktop/captured_images"  # 이미지를 저장할 폴더 경로
    os.makedirs(desktop_path, exist_ok=True)  # 디렉토리가 없으면 생성
    while capturing:  # capturing이 False로 설정될 때까지 실행
        ret, frame = cap.read()
        if ret:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            image_filename = os.path.join(desktop_path, f"captured_image_{timestamp}.jpg")
            cv2.imwrite(image_filename, frame)
            print(f"이미지가 {image_filename}로 저장되었습니다.")
        time.sleep(0.5)  # 0.5초마다 이미지 캡처

# 모터, 서보, 이미지 캡처를 제어하는 메인 루프
try:
    print("조작 방법:")
    print("W - 앞으로 이동, S - 뒤로 이동, + - 속도 증가, - - 속도 감소")
    print("A - 서보 왼쪽, D - 서보 오른쪽, X - 모터 정지, E - 종료, C - 서보 중앙으로 이동")

    # 서보의 중앙 각도 정의
    center_angle = 55  # 초기 중앙 위치 (30도와 80도 사이)
    current_speed = 30  # 초기 속도 (0에서 100)
    current_direction = "stop"  # 초기 방향
    servo_angle = center_angle  # 서보를 중앙 위치로 설정

    # 이미지 캡처 쓰레드 시작
    capturing = True
    capture_thread = threading.Thread(target=capture_images)
    capture_thread.start()

    while True:
        key = get_key()

        # DC 모터 제어
        if key == 'w':  # 앞으로 이동
            current_direction = "forward"
            dc_motor_control(current_direction, current_speed)
        elif key == 's':  # 뒤로 이동
            current_direction = "backward"
            dc_motor_control(current_direction, current_speed)
        elif key == 'x':  # 모터 정지
            current_direction = "stop"
            dc_motor_control(current_direction, 0)
        elif key == '+':  # 속도 증가
            if current_speed < 100:
                current_speed += 5
            print(f"속도가 {current_speed}로 증가했습니다.")
            dc_motor_control(current_direction, current_speed)
        elif key == '-':  # 속도 감소
            if current_speed > 0:
                current_speed -= 5
            print(f"속도가 {current_speed}로 감소했습니다.")
            dc_motor_control(current_direction, current_speed)

        # 서보 모터 제어
        elif key == 'a':  # 서보 왼쪽으로 이동
            servo_angle = max(30, servo_angle - 5)  # 각도를 30도 이하로 낮추지 않음
            servo_control(servo_angle)
        elif key == 'd':  # 서보 오른쪽으로 이동
            servo_angle = min(80, servo_angle + 5)  # 각도를 80도 이상으로 높이지 않음
            servo_control(servo_angle)

        # 서보를 중앙으로 이동
        elif key == 'c':  # 서보 중앙으로
            servo_angle = center_angle
            servo_control(servo_angle)

        # 프로그램 종료
        elif key == 'e':
            break

finally:
    # 이미지 캡처 중지
    capturing = False
    capture_thread.join()  # 캡처 쓰레드가 종료될 때까지 대기

    # 리소스 정리
    dc_motor_control("stop", 0)
    pwm_servo.stop()
    pwm_dc.stop()
    GPIO.cleanup()  # GPIO 핀 초기화
    cap.release()  # 카메라 해제
    cv2.destroyAllWindows()  # OpenCV 창 닫기
    print("프로그램이 종료되고 GPIO가 정리되었습니다.")
