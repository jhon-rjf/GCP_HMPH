import os
import cv2
import matplotlib.pyplot as plt

def load_yolo_labels(txt_file):
    with open(txt_file, 'r') as file:
        lines = file.readlines()
    labels = []
    for line in lines:
        parts = line.strip().split()
        label = int(parts[0])
        x_center = float(parts[1])
        y_center = float(parts[2])
        width = float(parts[3])
        height = float(parts[4])
        labels.append((label, x_center, y_center, width, height))
    return labels

def plot_bounding_boxes(image_path, labels):
    image = cv2.imread(image_path)
    image_height, image_width, _ = image.shape
    for label in labels:
        class_id, x_center, y_center, width, height = label
        x_center *= image_width
        y_center *= image_height
        width *= image_width
        height *= image_height
        x_min = int(x_center - width / 2)
        y_min = int(y_center - height / 2)
        x_max = int(x_center + width / 2)
        y_max = int(y_center + height / 2)
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
        cv2.putText(image, str(class_id), (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

def main():
    image_path = '/Users/jeong-yungeol/Desktop/vertexai/corwdhuman/train/Images/273271,1017c000ac1360b7.jpg'
    txt_file = '/Users/jeong-yungeol/Desktop/vertexai/annotation_test/273271,1017c000ac1360b7.txt'
    labels = load_yolo_labels(txt_file)
    plot_bounding_boxes(image_path, labels)

if __name__ == '__main__':
    main()

