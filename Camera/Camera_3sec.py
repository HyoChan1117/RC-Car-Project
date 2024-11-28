import cv2
import numpy as np
import subprocess
import shlex
import datetime
import time

# libcamera-vid 명령어로 실시간 카메라 스트림 설정
cmd = 'libcamera-vid --inline --nopreview -t 0 --codec mjpeg --width 640 --height 480 --framerate 30 -o - --camera 0'
# 명령어를 실행하여 출력과 오류를 파이프로 연결
process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 캡처 간격(초) 설정 및 마지막 캡처 시간을 현재 시간으로 초기화
capture_interval = 3  # 3초마다 캡처
last_capture_time = time.time()

# OpenCV 창 이름을 'frame'으로 설정하고 크기 조정
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
cv2.resizeWindow('frame', 640, 360)

try:
    buffer = b""  # 스트림 데이터를 임시로 저장할 버퍼
    while True:
        current_time = time.time()  # 현재 시간을 가져옴

        # 4096 바이트씩 스트림 데이터를 읽어 버퍼에 추가
        buffer += process.stdout.read(4096)
        
        # JPEG 이미지의 시작과 끝을 찾음
        a = buffer.find(b'\xff\xd8')  # JPEG 시작 바이트 위치
        b = buffer.find(b'\xff\xd9')  # JPEG 종료 바이트 위치

        # JPEG 이미지가 완성된 경우
        if a != -1 and b != -1:
            # JPEG 데이터를 추출하여 이미지로 사용
            jpg = buffer[a:b+2]
            # 사용된 데이터는 버퍼에서 제거하여 다음 이미지를 준비
            buffer = buffer[b+2:]

            # JPEG 데이터를 BGR 이미지로 디코딩
            bgr_frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

            # 디코딩이 성공했을 경우
            if bgr_frame is not None:
                # 화면에 이미지 표시
                cv2.imshow('frame', bgr_frame)

                # 주기적으로 이미지 캡처 및 저장
                if current_time - last_capture_time >= capture_interval:
                    # 파일명으로 사용할 현재 시간 문자열 생성
                    now = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
                    print("take picture:", now)  # 캡처 시각 출력
                    # 캡처한 이미지 저장
                    cv2.imwrite("./data/image/" + now + ".jpg", bgr_frame)
                    # 마지막 캡처 시간을 현재 시간으로 갱신
                    last_capture_time = current_time

                # 'q' 키를 누르면 루프 종료
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

finally:
    # libcamera-vid 프로세스를 종료하여 스트림을 중단
    process.terminate()
    # 모든 OpenCV 창을 닫고 리소스를 해제
    cv2.destroyAllWindows()