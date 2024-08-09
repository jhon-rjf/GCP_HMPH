#******
#filename: odgt_to_jsonl.py
#How to run: python odgt_to_jsonl.py <path_to_odgt_file> <path_to_output_jsonl> <bucket_name>
#dev: YunK
#******

import json
import sys

def get_ml_use(index, total_files):
    ratio = [1, 8, 1]  # test:train:validation ratio
    segment = total_files / sum(ratio)
    if index < segment:
        return "test"
    elif index < segment * (ratio[0] + ratio[1]):
        return "train"
    else:
        return "validation"

def odgt_to_jsonl(odgt_file, output_jsonl, bucket_name, num_files=4371, display_name="human"):
    jsonl_data = []

    with open(odgt_file, 'r') as file:
        lines = file.readlines()

    for index, line in enumerate(lines[:num_files]):
        entry = json.loads(line)
        original_image_name = entry["ID"] + ".jpg"  # 쉼표를 포함한 원래 파일명 사용
        image_gcs_uri = f"gs://{bucket_name}/{original_image_name}"
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
        
        ml_use = get_ml_use(index, num_files)
        data_item = {
            "imageGcsUri": image_gcs_uri,
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
    if len(sys.argv) != 4:
        print("Usage: python odgt_to_jsonl.py <path_to_odgt_file> <path_to_output_jsonl> <bucket_name>")
    else:
        odgt_file = sys.argv[1]
        output_jsonl = sys.argv[2]
        bucket_name = sys.argv[3]
        odgt_to_jsonl(odgt_file, output_jsonl, bucket_name)
