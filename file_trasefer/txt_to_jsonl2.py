import os
import json
import random
from pathlib import Path

# Define paths and parameters
yolo_directory = "/Users/jeong-yungeol/Desktop/vertexai/txt"
output_jsonl_file = "/Users/jeong-yungeol/Desktop/vertexai/output1.jsonl"
bucket_name = "anu_gcp_team2_dataset/image_500/Images/"
test_ratio = 0.1
val_ratio = 0.1

# Function to convert a single YOLO txt file to Vertex AI JSONL format
def convert_yolo_to_jsonl(txt_file, bucket_name):
    with open(txt_file, 'r') as f:
        annotations = []
        for line in f:
            parts = line.strip().split()
            label = int(parts[0])
            x_center, y_center, width, height = map(float, parts[1:])

            # Convert YOLO format to bounding box coordinates
            image_width, image_height = 800, 600  # Placeholder values; replace with actual image dimensions
            x_min = int((x_center - width / 2) * image_width)
            y_min = int((y_center - height / 2) * image_height)
            x_max = int((x_center + width / 2) * image_width)
            y_max = int((y_center + height / 2) * image_height)

            annotation = {
                "displayName": "person",
                "xMin": x_min,
                "yMin": y_min,
                "xMax": x_max,
                "yMax": y_max,
                "annotationResourceLabels": {
                    "aiplatform.googleapis.com/annotation_set_name": "person",
                    "env": "prod"
                }
            }
            annotations.append(annotation)

        image_file_name = os.path.basename(txt_file).replace('.txt', '.jpg')
        jsonl_entry = {
            "imageGcsUri": f"gs://{bucket_name}{image_file_name}",
            "boundingBoxAnnotations": annotations
        }
        return jsonl_entry

# Read all YOLO txt files and convert them to JSONL format
yolo_files = list(Path(yolo_directory).glob("*.txt"))
jsonl_entries = [convert_yolo_to_jsonl(txt_file, bucket_name) for txt_file in yolo_files]

# Split the dataset into train, val, and test sets
random.shuffle(jsonl_entries)
total_count = len(jsonl_entries)
test_count = int(total_count * test_ratio)
val_count = int(total_count * val_ratio)
train_count = total_count - test_count - val_count

test_data = jsonl_entries[:test_count]
val_data = jsonl_entries[test_count:test_count + val_count]
train_data = jsonl_entries[test_count + val_count:]

# Add the "ml_use" labels
for entry in test_data:
    entry["dataItemResourceLabels"] = {"aiplatform.googleapis.com/ml_use": "test"}
for entry in val_data:
    entry["dataItemResourceLabels"] = {"aiplatform.googleapis.com/ml_use": "val"}
for entry in train_data:
    entry["dataItemResourceLabels"] = {"aiplatform.googleapis.com/ml_use": "train"}

# Save the combined JSONL entries to the output file
with open(output_jsonl_file, 'w') as f:
    for entry in test_data + val_data + train_data:
        f.write(json.dumps(entry) + '\n')

print(f"Data has been converted and saved to {output_jsonl_file}")

