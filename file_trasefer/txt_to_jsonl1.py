import os
import json

def yolo_to_vertexai_jsonl(yolo_directory, output_jsonl):
    jsonl_data = []

    for filename in os.listdir(yolo_directory):
        if filename.endswith('.txt'):
            image_id = filename.replace('.txt', '')
            image_uri = f"gs://anu_gcp_team2_dataset/image_500/Images/{image_id}.jpg"

            with open(os.path.join(yolo_directory, filename), 'r') as file:
                lines = file.readlines()

            annotations = []
            for line in lines:
                parts = line.strip().split()
                class_id = int(parts[0])
                bbox = [float(part) for part in parts[1:]]

                annotation = {
                    "bbox": {
                        "normalizedVertices": [
                            {"x": bbox[0] - bbox[2]/2, "y": bbox[1] - bbox[3]/2},
                            {"x": bbox[0] + bbox[2]/2, "y": bbox[1] - bbox[3]/2},
                            {"x": bbox[0] + bbox[2]/2, "y": bbox[1] + bbox[3]/2},
                            {"x": bbox[0] - bbox[2]/2, "y": bbox[1] + bbox[3]/2}
                        ]
                    },
                    "annotationSpecId": class_id,
                    "displayName": "person"  # assuming all annotations are for people
                }
                annotations.append(annotation)

            vertexai_annotation = {
                "imageGcsUri": image_uri,
                "label": {
                    "annotations": annotations
                }
            }
            jsonl_data.append(vertexai_annotation)

    with open(output_jsonl, 'w') as jsonl_file:
        for entry in jsonl_data:
            jsonl_file.write(json.dumps(entry) + '\n')

# 예시 사용법
yolo_directory = '/Users/jeong-yungeol/Desktop/vertexai/txt'
output_jsonl = 'output.jsonl'

yolo_to_vertexai_jsonl(yolo_directory, output_jsonl)

