#******
#filename: predict_video_object_detection_sample.py
#How to run: python predict_video_object_detection_sample.py
#dev: YunK
#*******

import cv2
import base64
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

def predict_image_object_detection_sample(project, endpoint_id, location, image):
    client_options = {
        "api_endpoint": f"{location}-aiplatform.googleapis.com"
    }

    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    # The full resource name of the endpoint
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )

    # Encode the image content to base64
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

def process_video(video_path, project, endpoint_id, location):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * 2)  # 2초에 1프레임씩 처리

    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            predictions = predict_image_object_detection_sample(project, endpoint_id, location, frame)
            for prediction in predictions:
                bbox_count = len(prediction['bboxes'])
                print(f"Frame {frame_count}: human: {bbox_count}")
                # 프레임에 박스 수를 표시
                cv2.putText(frame, f"human: {bbox_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        frame_count += 1

        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    process_video(
    project: str = "YOUR_PROJECT_ID",
    endpoint_id: str = "YOUR_END_POINT_ID",
    location: str = "YOUR_PROJECT_LOCATION",
    filename: str = "YOUR_FILE_PATH"
    )

