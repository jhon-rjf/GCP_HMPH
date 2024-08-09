#******
#filename: visualize_labels.py
#How to run: python visualize_labels.py <input_jsonl_file> <input_image_file>
#dev: YunK
#******

import json
import cv2
import matplotlib.pyplot as plt
import sys

def visualize_labels(jsonl_file, image_file):
    with open(jsonl_file, 'r') as file:
        lines = file.readlines()

    for line in lines:
        entry = json.loads(line)
        image_path = entry.get('fpath')

        if image_path == image_file:
            labels = entry.get('gtboxes', [])
            image = cv2.imread(image_path)
            if image is None:
                print(f"이미지를 불러올 수 없습니다: {image_path}")
                continue

            for label in labels:
                box = label.get('box', [])
                if len(box) == 4:
                    x1, y1, x2, y2 = map(int, box)
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    if 'tag' in label:
                        cv2.putText(image, label['tag'], (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # 이미지를 RGB로 변환 (OpenCV는 BGR을 사용하므로)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Matplotlib을 사용하여 이미지 시각화
            plt.imshow(image)
            plt.axis('off')
            plt.show()
            return

    print(f"{image_file}에 대한 라벨 정보를 {jsonl_file}에서 찾을 수 없습니다.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("사용법: python visualize_labels.py <input_jsonl_file> <input_image_file>")
        sys.exit(1)

    input_jsonl_file = sys.argv[1]
    input_image_file = sys.argv[2]
    visualize_labels(input_jsonl_file, input_image_file)

