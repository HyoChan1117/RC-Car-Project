import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, models

# 데이터 경로
data_dir = "road_data"
images = []
labels = []

# 데이터 로드
label_map = {"left": 0, "straight": 1, "right": 2}
for file_name in os.listdir(data_dir):
    if file_name.endswith(".jpg"):
        img = cv2.imread(os.path.join(data_dir, file_name))
        img = cv2.resize(img, (128, 128))  # 이미지 크기 조정
        images.append(img)
        
        # 라벨 추출
        label = file_name.split("_")[1].split(".")[0]
        labels.append(label_map[label])

# 배열로 변환
images = np.array(images) / 255.0
labels = np.array(labels)

# 데이터 분리
X_train, X_val, y_train, y_val = train_test_split(images, labels, test_size=0.2, random_state=42)

# 모델 정의
model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 3)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(3, activation='softmax')  # 방향 분류 (좌, 직진, 우)
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# 모델 학습
model.fit(X_train, y_train, epochs=10, validation_data=(X_val, y_val), batch_size=32)

# 모델 저장
model.save("road_tracking_model.h5")
print("모델 저장 완료: road_tracking_model.h5")
