import os
import csv

# 데이터셋 디렉토리 생성
os.makedirs("dataset", exist_ok=True)
print("Dataset directory checked or created.")

# CSV 파일 경로 설정
csv_path = "dataset/line_tracking_data.csv"

# CSV 파일 초기화 (처음 실행할 때 열 이름 작성)
if not os.path.exists(csv_path):
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["image_path", "timestamp", "label_data"])
    print("CSV file created successfully.")

print("CSV file path:", csv_path)