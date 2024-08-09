import os
import json
import shutil
import sys

def rename_images(image_dir):
    image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
    new_names = {}
    
    for idx, image_file in enumerate(sorted(image_files), start=1):
        new_name = f"image{idx}.jpg"
        old_path = os.path.join(image_dir, image_file)
        new_path = os.path.join(image_dir, new_name)
        shutil.move(old_path, new_path)
        new_names[image_file] = new_name
        print(f"Renamed {image_file} to {new_name}")
    
    return new_names

def update_annotations_and_convert_to_jsonl(annotation_file, image_mapping, output_file):
    with open(annotation_file, 'r') as file:
        lines = file.readlines()
    
    updated_annotations = []
    
    for line in lines:
        data = json.loads(line)
        original_id = data["ID"]
        for old_name, new_name in image_mapping.items():
            if old_name in original_id:
                new_id = original_id.replace(old_name.split(",")[0], new_name.split(".")[0])
                data["ID"] = new_id
                break
        updated_annotations.append(data)
    
    with open(output_file, 'w') as file:
        for annotation in updated_annotations:
            file.write(json.dumps(annotation) + '\n')
    
    print(f"Updated JSONL file saved as {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python convert_odgt_to_jsonl.py annotation_Train.odgt Images updated_annotations.jsonl")
        sys.exit(1)
    
    annotation_file = sys.argv[1]
    image_dir = sys.argv[2]
    output_file = sys.argv[3]
    
    image_mapping = rename_images(image_dir)
    update_annotations_and_convert_to_jsonl(annotation_file, image_mapping, output_file)
