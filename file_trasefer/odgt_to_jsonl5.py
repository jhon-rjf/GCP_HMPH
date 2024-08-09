#******
#filename: odgt_to_jsonl.py
#How to run: python odgt_to_jsonl.py <path_to_odgt_file> <path_to_output_jsonl> <bucket_name> <ml_use>
#dev: YunK
#******

import json
import sys
import os

def odgt_to_jsonl(odgt_file, output_jsonl, bucket_name, ml_use):
    with open(odgt_file, 'r') as file:
        odgt_data = json.load(file)
    
    jsonl_data = []

    for entry in odgt_data:
        image_id = entry["ID"].split(",")[0]  # Assuming ID has the image filename without extension
        image_path = f"gs://{bucket_name}/{image_id}.jpg"
        bounding_box_annotations = []

        for box in entry["gtboxes"]:
            tag = box["tag"]
            fbox = box["fbox"]
            x_min = fbox[0]
            y_min = fbox[1]
            x_max = fbox[0] + fbox[2]
            y_max = fbox[1] + fbox[3]

            annotation = {
                "displayName": tag,
                "xMin": x_min,
                "yMin": y_min,
                "xMax": x_max,
                "yMax": y_max,
                "annotationResourceLabels": {
                    "aiplatform.googleapis.com/annotation_set_name": tag,
                    "env": "prod"
                }
            }
            bounding_box_annotations.append(annotation)
        
        data_item = {
            "imageGcsUri": image_path,
            "boundingBoxAnnotations": bounding_box_annotations,
            "dataItemResourceLabels": {
                "aiplatform.googleapis.com/ml_use": ml_use
            }
        }
        jsonl_data.append(data_item)
    
    with open(output_jsonl, 'w') as file:
        for entry in jsonl_data:
            file.write(json.dumps(entry) + '\n')
    
    print(f"Successfully converted ODGT to JSONL format and saved to {output_jsonl}")

# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python odgt_to_jsonl.py <path_to_odgt_file> <path_to_output_jsonl> <bucket_name> <ml_use>")
    else:
        odgt_file = sys.argv[1]
        output_jsonl = sys.argv[2]
        bucket_name = sys.argv[3]
        ml_use = sys.argv[4]  # "test", "train", or "validation"
        odgt_to_jsonl(odgt_file, output_jsonl, bucket_name, ml_use)
