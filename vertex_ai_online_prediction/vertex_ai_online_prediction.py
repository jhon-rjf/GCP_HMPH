import json
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.protobuf import json_format

def predict_image_object_detection_sample(
    project: str,
    endpoint_id: str,
    location: str,
    filename: str,
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}

    # Initialize the prediction client
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    # Read the image file
    with open(filename, "rb") as f:
        content = f.read()

    # Prepare the payload
    instance = predict.instance.ImageObjectDetectionPredictionInstance(
        content=content
    ).to_value()
    instances = [instance]

    # Set the parameters
    parameters = json_format.ParseDict({}, predict.params.ImageObjectDetectionPredictionParams(), ignore_unknown_fields=True)

    # Make the prediction request
    endpoint = client.endpoint_path(project=project, location=location, endpoint=endpoint_id)
    response = client.predict(endpoint=endpoint, instances=instances, parameters=parameters)
    
    # Print the prediction results
    print("Prediction results:")
    for prediction in response.predictions:
        print(json.dumps(json_format.MessageToDict(prediction), indent=2))

if __name__ == "__main__":
    project: str = "YOUR_PROJECT_ID",
    endpoint_id: str = "YOUR_END_POINT_ID",
    location: str = "YOUR_PROJECT_LOCATION",
    filename: str = "YOUR_FILE_PATH"  # replace this with your actual image file path

    predict_image_object_detection_sample(
        project=project,
        endpoint_id=endpoint_id,
        location=location,
        filename=filename
    )

