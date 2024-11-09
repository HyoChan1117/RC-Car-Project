import time
from adafruit_pca9685 import PCA9685
import board

# 유효한 I2C 포트를 사용하여 I2C 버스 초기화
i2c = board.I2C()  # SCL과 SDA 핀 사용

# PCA9685 초기화
pwm = PCA9685(i2c)

# 서보모터의 PWM 주파수 설정
pwm.frequency = 50  # 50Hz가 서보모터에 적합

# 서보모터를 제어하는 함수 정의
def set_servo_angle(channel, angle):
    min_pulse = 100  # 서보 모터의 최소 펄스 폭 (마이크로초)
    max_pulse = 1000  # 서보 모터의 최대 펄스 폭 (마이크로초)

    # 각도를 펄스 폭으로 변환
    pulse_us = min_pulse + (angle / 180.0) * (max_pulse - min_pulse)

    # 펄스 폭을 duty_cycle로 변환
    duty_cycle = int((pulse_us / (1000000 / pwm.frequency)) * 65535)

    pwm.channels[channel].duty_cycle = duty_cycle

# 서보모터 테스트 코드
try:
    angles = [0, 30, 45, 60, 90]  # 설정할 각도 리스트

    for angle in angles:
        print(f"서보모터를 {angle}도로 설정합니다.")
        set_servo_angle(0, angle)
        time.sleep(2)  # 각도 설정 후 2초 대기

except KeyboardInterrupt:
    print("프로그램 종료")

# PCA9685 종료
pwm.deinit()
