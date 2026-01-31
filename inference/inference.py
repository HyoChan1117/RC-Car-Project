import cv2
import numpy as np
from tensorflow.keras.models import load_model

# 모델 로드
model = load_model("road_tracking_model.h5")
label_map = {0: "left", 1: "straight", 2: "right"}

# 카메라 초기화
cap = cv2.VideoCapture(0)
print("실시간 추론을 시작합니다. 'q'를 눌러 종료하세요.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 이미지 전처리
    img = cv2.resize(frame, (128, 128)) / 255.0
    img = np.expand_dims(img, axis=0)  # 배치 차원 추가

    # 모델 추론
    prediction = model.predict(img)
    direction = label_map[np.argmax(prediction)]
    print(f"예측된 방향: {direction}")

    # 화면에 표시
    cv2.putText(frame, f"Direction: {direction}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Road View", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
