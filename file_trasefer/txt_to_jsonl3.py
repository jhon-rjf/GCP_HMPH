import os
import json
import random

def yolo_to_vertexai_jsonl(yolo_directory, output_jsonl, bucket_name, test_ratio=0.1, val_ratio=0.1):
    jsonl_data = []

    for filename in os.listdir(yolo_directory):
        if filename.endswith('.txt'):
            image_id = filename.replace('.txt', '')
            image_uri = f"gs://{bucket_name}/{image_id}.jpg"

            with open(os.path.join(yolo_directory, filename), 'r') as file:
                lines = file.readlines()

            annotations = []
            for line in lines:
                parts = line.strip().split()
                class_id = int(parts[0])
                bbox = [float(part) for part in parts[1:]]

                annotation = {
                    "displayName": "person",
                    "xMin": max(0, bbox[0] - bbox[2]/2),
                    "yMin": max(0, bbox[1] - bbox[3]/2),
                    "xMax": min(1, bbox[0] + bbox[2]/2),
                    "yMax": min(1, bbox[1] + bbox[3]/2),
                    "annotationResourceLabels": {
                        "aiplatform.googleapis.com/annotation_set_name": "person",
                        "env": "prod"
                    }
                }
                annotations.append(annotation)

            vertexai_annotation = {
                "imageGcsUri": image_uri,
                "boundingBoxAnnotations": annotations
            }
            jsonl_data.append(vertexai_annotation)

    # Shuffle and split the data
    random.shuffle(jsonl_data)
    total_count = len(jsonl_data)
    test_count = int(total_count * test_ratio)
    val_count = int(total_count * val_ratio)

    test_data = jsonl_data[:test_count]
    val_data = jsonl_data[test_count:test_count + val_count]
    train_data = jsonl_data[test_count + val_count:]

    # Add the "ml_use" labels
    for entry in test_data:
        entry["dataItemResourceLabels"] = {"aiplatform.googleapis.com/ml_use": "test"}
    for entry in val_data:
        entry["dataItemResourceLabels"] = {"aiplatform.googleapis.com/ml_use": "val"}
    for entry in train_data:
        entry["dataItemResourceLabels"] = {"aiplatform.googleapis.com/ml_use": "train"}

    # Save the combined JSONL entries to the output file
    with open(output_jsonl, 'w') as jsonl_file:
        for entry in test_data + val_data + train_data:
            jsonl_file.write(json.dumps(entry) + '\n')

# 예시 사용법
yolo_directory = '/Users/jeong-yungeol/Desktop/vertexai/odgt2txt/yolo_class_0'
output_jsonl = '/Users/jeong-yungeol/Desktop/vertexai/odgt2jsonl15000.jsonl'
bucket_name = 'anu_gcp_team2_dataset/CrowdHuman_dataset_train/Images'

yolo_to_vertexai_jsonl(yolo_directory, output_jsonl, bucket_name)

