#******
#filename: vertex_ai_prediction_sample.py
#How to run: python vertex_ai_prediction_sample.py
#dev: YunK
#******

from google.cloud import aiplatform
import base64

# Google Cloud Vertex AI 설정
PROJECT_ID = 'YOUY_PROJECT_ID'
REGION = 'YOUR_PROJECT_REGION'
ENDPOINT_ID = 'YOUR_ENDPOINT_ID'


# 이미지 데이터를 base64로 인코딩
def read_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Vertex AI 예측 요청
def predict_image_object_detection_sample(project, endpoint_id, location, filename):
    aiplatform.init(project=project, location=location)
    endpoint = aiplatform.Endpoint(endpoint_name=f'projects/{project}/locations/{location}/endpoints/{endpoint_id}')
    
    instance = {
        "content": read_image(filename),
        "mimeType": "image/jpeg"
    }
    
    response = endpoint.predict(instances=[instance])
    
    predictions = []
    for prediction in response.predictions:
        predictions.append(prediction)
    return predictions

def main():
    image_path = "./images/image.jpg"
    predictions = predict_image_object_detection_sample(
        project=PROJECT_ID,
        endpoint_id=ENDPOINT_ID,
        location=REGION,
        filename=image_path
    )
    for prediction in predictions:
        print("Prediction:", prediction)

if __name__ == "__main__":
    main()
