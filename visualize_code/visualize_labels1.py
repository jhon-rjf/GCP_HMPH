import os
import json
import cv2
import matplotlib.pyplot as plt

# Define paths
odgt_file_path = '/Users/jeong-yungeol/Desktop/vertexai/annotation_val1.odgt'
images_folder_path = '/Users/jeong-yungeol/Desktop/vertexai/corwdhuman/Images'

def load_odgt(odgt_file_path):
    with open(odgt_file_path, 'r') as file:
        lines = file.readlines()
        data = [json.loads(line) for line in lines]
    return data

def display_labeled_image(image_path, label_data):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB for displaying with matplotlib
    
    if 'gtboxes' not in label_data:
        print(f"No gtboxes found for image {image_path}")
        return
    
    for box in label_data['gtboxes']:
        bbox = box['fbox']  # Use full body box for drawing
        tag = box['tag']
        
        # Draw bounding box
        top_left = (int(bbox[0]), int(bbox[1]))
        bottom_right = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        cv2.rectangle(image, top_left, bottom_right, (255, 0, 0), 2)
        
        # Put tag text
        cv2.putText(image, tag, (int(bbox[0]), int(bbox[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # Display the image
    plt.figure(figsize=(10, 10))
    plt.imshow(image)
    plt.axis('off')
    plt.show()

def visualize_labels(odgt_file_path, images_folder_path):
    data = load_odgt(odgt_file_path)
    
    for entry in data:
        image_id = entry['ID']
        image_path = os.path.join(images_folder_path, f'{image_id}.jpg')
        
        if os.path.exists(image_path):
            display_labeled_image(image_path, entry)
        else:
            print(f'Image {image_id}.jpg not found.')

# Run the visualization function
visualize_labels(odgt_file_path, images_folder_path)
