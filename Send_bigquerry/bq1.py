#******
#filename: bq1.py
#How to run: bq1.py
#dev: YunK
#*******

import cv2
import base64
from google.cloud import aiplatform
from google.cloud import bigquery
from google.cloud.aiplatform.gapic.schema import predict
from google.protobuf.struct_pb2 import Value
from datetime import datetime, timezone, timedelta

def predict_image_object_detection_sample(project, endpoint_id, location, image):
    client_options = {
        "api_endpoint": f"{location}-aiplatform.googleapis.com"
    }

    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )

    _, buffer = cv2.imencode('.jpg', image)
    encoded_content = base64.b64encode(buffer).decode("utf-8")

    instance = predict.instance.ImageObjectDetectionPredictionInstance(
        content=encoded_content
    ).to_value()

    instances = [instance]
    parameters = predict.params.ImageObjectDetectionPredictionParams(
        confidence_threshold=0.5
    ).to_value()

    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )

    return response.predictions

def insert_into_bigquery(number, timestamp, person_count, project_id, dataset_id, table_id):
    client = bigquery.Client(project=project_id)
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)

    rows_to_insert = [
        {u"number": number, u"timestamp": timestamp, u"person_count": person_count}
    ]

    errors = client.insert_rows_json(table, rows_to_insert)
    if errors:
        print(f"Encountered errors while inserting rows: {errors}")
    else:
        print(f"Inserted {len(rows_to_insert)} rows into {dataset_id}.{table_id}.")

def process_video(video_path, project, endpoint_id, location, project_id, dataset_id, table_id):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps)  # Process 1 frame per second

    frame_count = 0
    number = 1

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Reached the end of the video or failed to read frame.")
            break

        if frame_count % frame_interval == 0:
            predictions = predict_image_object_detection_sample(project, endpoint_id, location, frame)
            for prediction in predictions:
                bbox_count = len(prediction['bboxes'])
                current_time = datetime.now(timezone(timedelta(hours=9))).isoformat()
                print(f"{number}, {current_time}, {bbox_count}")
                insert_into_bigquery(number, current_time, bbox_count, project_id, dataset_id, table_id)
                number += 1

        frame_count += 1

    cap.release()

if __name__ == "__main__":
    process_video(
        video_path="YOUR_LOCAL_VIDEO_PATH",
        project="YOUR_VERTEX_AI_PROJECT_ID",
        endpoint_id="YOUR_VERTEX_AI_ENDPOINT_ID",
        location="YOUR_PROJECT_LOCATION",
        project_id="YOUR_PROJECT_ID",
        dataset_id="YOUR_BQ_DATASET_ID",
        table_id="YOUR_BQ_TABLE_ID"
    )
