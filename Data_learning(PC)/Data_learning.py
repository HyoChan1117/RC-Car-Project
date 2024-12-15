import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split
import os
import cv2
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Dropout

# === 데이터 로드 함수 ===
def load_processed_data(data_path, image_size):
    X = []
    y = []
    classes = ["left", "straight", "right"]
    class_indices = {cls: idx for idx, cls in enumerate(classes)}
    for cls in classes:
        cls_path = os.path.join(data_path, cls)
        for img_name in os.listdir(cls_path):
            img_path = os.path.join(cls_path, img_name)
            img = cv2.imread(img_path)
            img = cv2.resize(img, image_size)
            img = img / 255.0
            X.append(img)
            y.append(class_indices[cls])
    return np.array(X), np.array(y)

# 데이터 설정
data_path = "C:\\test\\processed_images"
image_size = (64, 64)
X, y = load_processed_data(data_path, image_size)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# 원-핫 인코딩
y_train = tf.keras.utils.to_categorical(y_train, num_classes=3)
y_val = tf.keras.utils.to_categorical(y_val, num_classes=3)

# === 모델 설계 ===
model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    Dropout(0.5),

    tf.keras.layers.Dense(3, activation='softmax')
])

# === 모델 컴파일 ===
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# === EarlyStopping 설정 ===
early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

# === 모델 훈련 ===
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    callbacks=[early_stopping]  # EarlyStopping 콜백 추가
)

# === 모델 평가 ===
loss, accuracy = model.evaluate(X_val, y_val)
print(f"검증 데이터 손실: {loss:.4f}")
print(f"검증 데이터 정확도: {accuracy * 100:.2f}%")

# === 모델 저장 ===
model.save("C:\\test\\lane_following_model.h5")
print("모델 저장 완료!")
