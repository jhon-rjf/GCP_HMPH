# ******
# filename: object_detection_visualization.py
# How to run: python object_detection_visualization.py
# dev: YunK
# *******

import cv2
import base64
import matplotlib.pyplot as plt
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict

def predict_image_object_detection_sample(
    project: str,
    endpoint_id: str,
    location: str,
    filename: str
):
    client_options = {"api_endpoint": f"{location}-aiplatform.googleapis.com"}
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    with open(filename, "rb") as f:
        content = f.read()
    
    encoded_content = base64.b64encode(content).decode('utf-8')
    
    instance = predict.instance.ImageObjectDetectionPredictionInstance(
        content=encoded_content,
    ).to_value()
    
    instances = [instance]
    parameters = predict.params.ImageObjectDetectionPredictionParams(
        confidence_threshold=0.5,
        max_predictions=5,
    ).to_value()
    
    endpoint = client.endpoint_path(
        project=project,
        location=location,
        endpoint=endpoint_id,
    )
    
    response = client.predict(
        endpoint=endpoint,
        instances=instances,
        parameters=parameters,
    )
    
    print("Full Response:")
    for prediction in response.predictions:
        for key, value in prediction.items():
            print(f"{key}: {value}")

    return response.predictions

def draw_bounding_boxes(image_path, predictions):
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    for prediction in predictions:
        print("Prediction:", prediction)  # Debug print
        for i, bbox in enumerate(prediction["bboxes"]):
            x_min, x_max, y_min, y_max = bbox[0] * width, bbox[2] * width, bbox[1] * height, bbox[3] * height
            cv2.rectangle(image, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
            label = prediction["displayNames"][i]
            score = prediction.get("scores", [None] * len(prediction["displayNames"]))[i]
            cv2.putText(image, f'{label} ({score:.2f})', (int(x_min), int(y_min) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Convert BGR to RGB for displaying with matplotlib
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(10, 10))
    plt.imshow(image_rgb)
    plt.axis("off")
    plt.show()

# 지정된 프로젝트 ID, 엔드포인트 ID, 위치 및 이미지 파일 경로
project: str = "YOUR_PROJECT_ID",
endpoint_id: str = "YOUR_END_POINT_ID",
location: str = "YOUR_PROJECT_LOCATION",
filename: str = "YOUR_FILE_PATH"

# 예측 요청 및 바운딩 박스 시각화
predictions = predict_image_object_detection_sample(
    project=project_id,
    endpoint_id=endpoint_id,
    location=location,
    filename=image_path
)

draw_bounding_boxes(image_path, predictions)

