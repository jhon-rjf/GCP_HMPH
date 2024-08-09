import os
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from pathlib import Path

def visualize_yolo_labels(image_path, label_path):
    # 이미지 열기
    img = Image.open(image_path)
    width, height = img.size

    fig, ax = plt.subplots(1)
    ax.imshow(img)

    # 라벨 파일 열기
    with open(label_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        class_id, center_x, center_y, box_width, box_height = map(float, line.strip().split())
        # YOLO 형식에서 절대 좌표로 변환
        center_x *= width
        center_y *= height
        box_width *= width
        box_height *= height

        # 경계 상자의 왼쪽 위 좌표 계산
        x = center_x - (box_width / 2)
        y = center_y - (box_height / 2)

        # 경계 상자 그리기
        rect = patches.Rectangle((x, y), box_width, box_height, linewidth=2, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

        # 클래스 ID 텍스트 표시
        plt.text(x, y, f'Class: {int(class_id)}', color='white', fontsize=12, backgroundcolor='red')

    plt.show()

# 이미지 및 라벨 경로 설정
image_file = '/Users/jeong-yungeol/Desktop/vertexai/corwdhuman/images/val/273271,1bd660006ab0ac6a.jpg'  # 여기에 이미지 파일 경로를 입력하세요
label_file = '/Users/jeong-yungeol/Desktop/vertexai/txt/273271,1bd660006ab0ac6a.txt'  # 여기에 라벨 파일 경로를 입력하세요

visualize_yolo_labels(image_file, label_file)

