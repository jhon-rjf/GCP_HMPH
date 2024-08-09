# ******
# filename: object_detection_visualization.py
# How to run: python object_detection_visualization.py
# dev: YunK
# *******

import cv2
import base64
import json
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
        bboxes = prediction["bboxes"]
        displayNames = prediction["displayNames"]
        confidences = prediction.get("confidences", [None] * len(displayNames))

        for i, bbox in enumerate(bboxes):
            # 바운딩 박스 좌표 변환 시도 (정규화된 값을 이미지 픽셀 좌표로 변환)
            x_min, y_min, x_max, y_max = bbox  # 기본 형식
            x_min2, y_min2, x_max2, y_max2 = y_min, x_min, y_max, x_max  # 다른 형식
            x_min3, y_min3, x_max3, y_max3 = x_min, y_max, x_max, y_min  # 또 다른 형식
            x_min4, y_min4, x_max4, y_max4 = y_max, x_min, y_min, x_max  # 또 다른 형식

            # 기본 형식
            x_min, x_max = x_min * width, x_max * width
            y_min, y_max = y_min * height, y_max * height
            print(f"Original bbox: {bbox}")
            print(f"Transformed bbox: ((int(x_min), int(y_min)), (int(x_max), int(y_max)))")
            cv2.rectangle(image, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
            label = displayNames[i]
            score = confidences[i]
            if score is not None:
                text = f'{label} ({score:.2f})'
            else:
                text = label
            cv2.putText(image, text, (int(x_min), int(y_min) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # 다른 형식
            x_min2, x_max2 = x_min2 * width, x_max2 * width
            y_min2, y_max2 = y_min2 * height, y_max2 * height
            print(f"Original bbox (alt): {bbox}")
            print(f"Transformed bbox (alt): ((int(x_min2), int(y_min2)), (int(x_max2), int(y_max2)))")
            cv2.rectangle(image, (int(x_min2), int(y_min2)), (int(x_max2), int(y_max2)), (255, 0, 0), 2)
            label = displayNames[i]
            score = confidences[i]
            if score is not None:
                text = f'{label} ({score:.2f})'
            else:
                text = label
            cv2.putText(image, text, (int(x_min2), int(y_min2) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

            # 또 다른 형식
            x_min3, x_max3 = x_min3 * width, x_max3 * width
            y_min3, y_max3 = y_min3 * height, y_max3 * height
            print(f"Original bbox (alt2): {bbox}")
            print(f"Transformed bbox (alt2): ((int(x_min3), int(y_min3)), (int(x_max3), int(y_max3)))")
            cv2.rectangle(image, (int(x_min3), int(y_min3)), (int(x_max3), int(y_max3)), (0, 0, 255), 2)
            label = displayNames[i]
            score = confidences[i]
            if score is not None:
                text = f'{label} ({score:.2f})'
            else:
                text = label
            cv2.putText(image, text, (int(x_min3), int(y_min3) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            # 또 다른 형식
            x_min4, x_max4 = x_min4 * width, x_max4 * width
            y_min4, y_max4 = y_min4 * height, y_max4 * height
            print(f"Original bbox (alt3): {bbox}")
            print(f"Transformed bbox (alt3): ((int(x_min4), int(y_min4)), (int(x_max4), int(y_max4)))")
            cv2.rectangle(image, (int(x_min4), int(y_min4)), (int(x_max4), int(y_max4)), (0, 255, 255), 2)
            label = displayNames[i]
            score = confidences[i]
            if score is not None:
                text = f'{label} ({score:.2f})'
            else:
                text = label
            cv2.putText(image, text, (int(x_min4), int(y_min4) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

    # Convert BGR to RGB for displaying with matplotlib
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(10, 10))
    plt.imshow(image_rgb)
    plt.axis("off")
    plt.show()

# 로컬 파일 경로로 수정
project_id = "YOUR_PROJECT_ID",
endpoint_id = "YOUR_END_POINT_ID",
location = "YOUR_PROJECT_LOCATION",
image_path = "YOUR_FILE_PATH"

# 예측 요청 및 바운딩 박스 시각화
predictions = predict_image_object_detection_sample(
    project=project_id,
    endpoint_id=endpoint_id,
    location=location,
    filename=image_path
)

draw_bounding_boxes(image_path, predictions)

