#******
#filename: predict_image_object_detection_sample.py
#How to run: python predict_image_object_detection_sample.py
#dev: YunK
#*******

from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
import io
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
import base64
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

def predict_image_object_detection_sample(
    project: str = "YOUR_PROJECT_ID",
    endpoint_id: str = "YOUR_END_POINT_ID",
    location: str = "YOUR_PROJECT_LOCATION",
    filename: str = "YOUR_FILE_PATH"
):
    client_options = {
        "api_endpoint": f"{location}-aiplatform.googleapis.com"
    }

    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    # The full resource name of the endpoint
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )

    with io.open(filename, "rb") as f:
        content = f.read()

    # Encode the image content to base64
    encoded_content = base64.b64encode(content).decode("utf-8")

    instance = predict.instance.ImageObjectDetectionPredictionInstance(
        content=encoded_content
    ).to_value()

    instances = [instance]
    parameters = predict.params.ImageObjectDetectionPredictionParams(
        confidence_threshold=0.5
        # max_predictions 파라미터를 제거하여 모든 예측을 수용
    ).to_value()

    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )

    print("response")
    print(" deployed_model_id:", response.deployed_model_id)

    predictions = response.predictions
    for prediction in predictions:
        print(" prediction:", dict(prediction))
        display_predictions(filename, prediction)


def display_predictions(image_path, prediction):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    
    bboxes = prediction['bboxes']
    confidences = prediction['confidences']
    display_names = prediction['displayNames']
    
    # 바운딩 박스의 개수를 출력
    bbox_count = len(bboxes)
    print(f"Number of bounding boxes: {bbox_count}")
    
    for bbox, confidence, display_name in zip(bboxes, confidences, display_names):
        left, top, right, bottom = (
            bbox[0] * image.width,
            bbox[1] * image.height,
            bbox[2] * image.width,
            bbox[3] * image.height,
        )
        draw.rectangle([left, top, right, bottom], outline="red", width=3)
        text = f"{display_name}: {confidence:.2f}"
        text_size = draw.textsize(text, font=font)
        draw.rectangle([left, top, left + text_size[0], top - text_size[1]], fill="red")
        draw.text((left, top - text_size[1]), text, fill="white", font=font)
    
    plt.figure(figsize=(12, 12))
    plt.imshow(image)
    plt.axis("off")
    plt.show()

# Example of how to run the function
if __name__ == "__main__":
    predict_image_object_detection_sample(
    project: str = "YOUR_PROJECT_ID",
    endpoint_id: str = "YOUR_END_POINT_ID",
    location: str = "YOUR_PROJECT_LOCATION",
    filename: str = "YOUR_FILE_PATH"
    )

