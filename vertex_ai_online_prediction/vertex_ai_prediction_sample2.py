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

    instance = predict.instance.ImageObjectDetectionPredictionInstance(
        content=content
    ).to_value()

    instances = [instance]
    parameters = predict.params.ImageObjectDetectionPredictionParams(
        confidence_threshold=0.5, max_predictions=5
    ).to_value()

    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )

    print("response")
    print(" deployed_model_id:", response.deployed_model_id)

    predictions = response.predictions
    for prediction in predictions:
        print(" prediction:", dict(prediction))

# Example of how to run the function
if __name__ == "__main__":
    predict_image_object_detection_sample(
            project: str = "YOUR_PROJECT_ID",
            endpoint_id: str = "YOUR_END_POINT_ID",
            location: str = "YOUR_PROJECT_LOCATION",
            filename: str = "YOUR_FILE_PATH"
    )
