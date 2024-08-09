import json

# Define paths
odgt_file_path = '/Users/jeong-yungeol/Desktop/vertexai/annotation_val1.odgt'
output_jsonl_file_path = '/Users/jeong-yungeol/Desktop/vertexai/val.jsonl'
gcs_bucket_url = 'gs://anu_gcp_team2_dataset/image_500/Images'

def load_odgt(odgt_file_path):
    with open(odgt_file_path, 'r') as file:
        lines = file.readlines()
        data = [json.loads(line) for line in lines]
    return data

def convert_to_vertex_ai_format(data):
    vertex_ai_data = []
    
    for entry in data:
        image_id = entry['ID']
        image_url = f"{gcs_bucket_url}/{image_id}.jpg"
        
        annotations = []
        for box in entry['gtboxes']:
            if box['tag'] == 'person':
                fbox = box['fbox']
                annotations.append({
                    "type": "bounding-box",
                    "label": "person",
                    "coordinates": {
                        "x": fbox[0],
                        "y": fbox[1],
                        "width": fbox[2],
                        "height": fbox[3]
                    }
                })
        
        vertex_ai_data.append({
            "image_url": image_url,
            "annotations": annotations
        })
    
    return vertex_ai_data

def save_as_jsonl(data, output_jsonl_file_path):
    with open(output_jsonl_file_path, 'w') as file:
        for entry in data:
            file.write(json.dumps(entry) + '\n')

# Run the conversion process
data = load_odgt(odgt_file_path)
filtered_data = convert_to_vertex_ai_format(data)
save_as_jsonl(filtered_data, output_jsonl_file_path)

print(f"Conversion complete. The output file is saved at {output_jsonl_file_path}")
