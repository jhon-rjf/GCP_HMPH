#******
#filename: yolo_to_jsonl.py
#How to run: python yolo_to_jsonl.py <path_to_yolo_folder> <path_to_output_jsonl>
#dev: YunK
#******

import os
import json

def get_ml_use(index, total_files):
    ratio = [1, 8, 1]  # test:train:validation ratio
    segment = total_files / sum(ratio)
    if index < segment:
        return "test"
    elif index < segment * (ratio[0] + ratio[1]):
        return "train"
    else:
        return "validation"

def yolo_to_jsonl(yolo_folder, output_jsonl, num_files=500, display_name="human"):
    # Prepare the expected file names in the format image1.txt, image2.txt, ..., image500.txt
    yolo_files = [f"image{i}.txt" for i in range(1, num_files + 1)]
    
    jsonl_data = []
    
    for index, filename in enumerate(yolo_files):
        yolo_path = os.path.join(yolo_folder, filename)
        
        if os.path.isfile(yolo_path):
            image_name = filename.replace('.txt', '.jpg')
            image_path = f"gs://anu_gcp_team2_dataset/image(500|13000)/{image_name}"
            
            bounding_box_annotations = []
            
            with open(yolo_path, 'r') as yolo_file:
                for line in yolo_file:
                    parts = line.strip().split()
                    if len(parts) != 5:
                        print(f"Skipping invalid line in {filename}: {line}")
                        continue
                    
                    class_id, x_center, y_center, width, height = map(float, parts)
                    
                    x_min = x_center - width / 2
                    x_max = x_center + width / 2
                    y_min = y_center - height / 2
                    y_max = y_center + height / 2
                    
                    annotation = {
                        "displayName": display_name,
                        "xMin": x_min,
                        "yMin": y_min,
                        "xMax": x_max,
                        "yMax": y_max,
                        "annotationResourceLabels": {
                            "aiplatform.googleapis.com/annotation_set_name": display_name,
                            "env": "prod"
                        }
                    }
                    bounding_box_annotations.append(annotation)
            
            ml_use = get_ml_use(index, num_files)
            data_item = {
                "imageGcsUri": image_path,
                "boundingBoxAnnotations": bounding_box_annotations,
                "dataItemResourceLabels": {
                    "aiplatform.googleapis.com/ml_use": ml_use
                }
            }
            jsonl_data.append(data_item)
        else:
            print(f"Warning: {yolo_path} does not exist and will be skipped.")
    
    with open(output_jsonl, 'w') as file:
        for entry in jsonl_data:
            file.write(json.dumps(entry) + '\n')
    
    print(f"Successfully converted {min(num_files, len(jsonl_data))} YOLO files to JSONL format and saved to {output_jsonl}")

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python yolo_to_jsonl.py <path_to_yolo_folder> <path_to_output_jsonl>")
    else:
        yolo_folder = sys.argv[1]
        output_jsonl = sys.argv[2]
        yolo_to_jsonl(yolo_folder, output_jsonl)

