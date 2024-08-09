#******
#filename: predict_video_object_detection_sample.py
#How to run: python predict_video_object_detection_sample.py
#dev: YunK
#*******

import cv2
import base64
import io
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
from PIL import Image, ImageDraw, ImageFont

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

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        predictions = predict_image_object_detection_sample(project, endpoint_id, location, frame)

        for prediction in predictions:
            frame = display_predictions(frame, prediction)

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def display_predictions(frame, prediction):
    draw = ImageDraw.Draw(Image.fromarray(frame))
    font = ImageFont.load_default()

    bboxes = prediction['bboxes']
    confidences = prediction['confidences']
    display_names = prediction['displayNames']

    bbox_count = len(bboxes)
    text = f"human: {bbox_count}"
    
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    for bbox, confidence, display_name in zip(bboxes, confidences, display_names):
        left, top, right, bottom = (
            int(bbox[0] * frame.shape[1]),
            int(bbox[1] * frame.shape[0]),
            int(bbox[2] * frame.shape[1]),
            int(bbox[3] * frame.shape[0]),
        )
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        label = f"{display_name}: {confidence:.2f}"
        cv2.putText(frame, label, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
    
    return frame

if __name__ == "__main__":
    process_video(
    project: str = "YOUR_PROJECT_ID",
    endpoint_id: str = "YOUR_END_POINT_ID",
    location: str = "YOUR_PROJECT_LOCATION",
    filename: str = "YOUR_FILE_PATH"
    )

