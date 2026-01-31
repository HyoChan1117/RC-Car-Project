# 자동운전차 프로젝트 (Self-Driving RC Car)

딥러닝을 활용한 차선 인식 및 실시간 제어 라인트래킹 RC Car 프로젝트

## 구현 영상

<p align="center">
  <img src="images/demo.gif" alt="자율주행 데모" width="600">
</p>

## 프로젝트 목적

영상을 이용한 **차선 인식**과 **실시간 제어**의 라인트래킹 시스템 구현

- 카메라 영상을 입력하여 모델이 차선을 인식
- 인식 결과를 바탕으로 서보모터 각도를 실시간 제어
- **딥러닝(CNN)을 활용한 자동운전 시스템**

## 주요 기술

| 플랫폼 | 언어 | 딥러닝 프레임워크 |
|--------|------|-------------------|
| Raspberry Pi | Python | TensorFlow / Keras |

## 개발 기간

**2024년 10월 6일 ~ 12월 15일**

- H/W 설계 및 개발환경 구축
- 주행 알고리즘 개발, 데이터 수집 및 전처리
- DL 모델의 학습 및 추론 구현

## 기술 선정: Raspberry Pi vs Jetson

초기 안정성과 학습 효율을 고려하여 **Raspberry Pi**를 채용

| 비교 항목 | Raspberry Pi | Jetson |
|-----------|--------------|--------|
| 제어/모델 실행환경 구축 | 용이 | 복잡 |
| 도입 난이도 | 낮음 | 높음 |
| 자료 및 샘플 | 풍부 | 상대적으로 적음 |
| 개발환경 구축 | 간단하고 신속 | 시간 소요 |

## 프로젝트 구조

```
RC-Car-Project/
├── All_moter_test/     # 서보모터 + DC모터 통합 테스트
├── Camera/             # 카메라 테스트 코드
├── Data_preprocessing/ # 이미지 전처리
├── DC/                 # DC 모터 제어 테스트
├── inference/          # 실시간 추론
├── learning/           # CNN 모델 학습
├── Motor_Camera/       # 데이터 수집 (모터 제어 + 카메라)
└── Servo/              # 서보모터 제어 테스트
```

---

## 프로젝트 실장 (제1차 시행)

### 1. 하드웨어 설계 및 조립

DL 추론환경을 고려한 임베디드 H/W 시스템 설계

- 영상 입력 및 모터 제어용 배선 구성
- Raspberry Pi 및 주변기기 연결
- 안정적인 전원 공급 구성

→ **실시간 주행이 가능한 H/W 환경 구축**

#### 하드웨어 배선도

<p align="center">
  <img src="images/HW.png" alt="하드웨어 배선도" width="500">
</p>

#### 부품 목록
- Raspberry Pi
- USB 웹캠
- 서보모터 (조향용)
- DC 모터 + L298N 모터 드라이버 (구동용)

#### GPIO 핀 연결
| 부품 | GPIO 핀 |
|------|---------|
| 서보모터 (PWM) | GPIO 12 |
| DC모터 IN1 | GPIO 17 |
| DC모터 IN2 | GPIO 27 |
| DC모터 ENA (PWM) | GPIO 18 |

### 2. 데이터 수집 및 전처리

학습용 데이터의 수집 및 전처리 실시

#### 데이터 수집
키보드로 RC Car를 수동 조종하면서 카메라 이미지를 자동 저장

```bash
python Motor_Camera/Data_collecting_code.py
```

| 키 | 동작 |
|----|------|
| ↑ | 전진 (속도 증가) |
| ↓ | 감속 |
| ← | 좌회전 |
| → | 우회전 |
| Space | 정지 |
| ESC | 종료 |

이미지는 조향 각도에 따라 `left/`, `straight/`, `right/` 폴더에 자동 분류

#### 조향 각도 범위

| 방향 | 서보모터 각도 |
|------|---------------|
| 좌회전 (left) | 0° ~ 20° |
| 직진 (straight) | 21° ~ 40° |
| 우회전 (right) | 41° ~ 60° |

#### 데이터 전처리
수집된 이미지를 학습에 적합하도록 전처리

```bash
python Data_preprocessing/data_processing.py
```

| 단계 | 처리 내용 |
|------|-----------|
| 1 | 불필요 영역 제거 (상단 30%) |
| 2 | 그레이스케일 변환 |
| 3 | 가우시안 블러 |
| 4 | 이진화 (Thresholding) |
| 5 | 모델 입력 사이즈에 맞춘 리사이즈 |

→ **DL 학습에 적합한 입력 데이터셋 구축**

### 3. 모델 학습

CNN 기반 자동운전 모델 설계 및 학습

```bash
python learning/Data_learning.py
```

#### 모델 구조
```
Input (64x64x3)
    ↓
Conv2D (32, 3x3) → ReLU → MaxPooling → Dropout(0.25)
    ↓
Conv2D (64, 3x3) → ReLU → MaxPooling → Dropout(0.25)
    ↓
Flatten → Dense (128) → ReLU → Dropout(0.5)
    ↓
Dense (3) → Softmax
    ↓
Output: [left, straight, right]
```

### 4. 실시간 추론

학습된 모델을 Raspberry Pi 환경에서 실시간 추론

```bash
python inference/inference.py
```

---

## 제1차 시행 결과

### 결과: 실패

**차선을 거의 인식하지 못함**

### 실패 원인 분석

| 문제점 | 설명 |
|--------|------|
| 데이터량 부족 | 학습 데이터가 충분하지 않음 |
| CPU 처리의 한계 | Raspberry Pi CPU로는 실시간 추론이 어려움 |
| 추론 엔진 미사용 | 모델 최적화 없이 raw TensorFlow 사용 |

→ **시스템 전체 환경 개선의 필요성**

---

## 재도전 계획 (제2차 시행)

### Jetson Nano를 활용한 자동운전차

| 개선 항목 | 내용 |
|-----------|------|
| 데이터 확장 | 확장된 데이터셋으로 모델 재학습 |
| GPU 가속 | GPU를 활용한 실시간 추론 환경 구축 |
| 모델 최적화 | TensorRT 적용으로 추론 속도 향상 |

→ **GPU 가속 환경에서 재도전**

---

## 의존성 설치

```bash
pip install tensorflow numpy opencv-python scikit-learn pynput RPi.GPIO
```

## 요구사항

- Python 3.7+
- TensorFlow 2.x
- OpenCV
- Raspberry Pi OS (제1차) / JetPack (제2차)
