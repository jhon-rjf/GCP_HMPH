import numpy as np
from flask import Flask, render_template, Response, request, jsonify
from flask_socketio import SocketIO, emit
import cv2
import time
from google.cloud import aiplatform, bigquery, storage
import base64
from google.cloud.aiplatform.gapic.schema import predict
from datetime import datetime, timezone, timedelta
import threading
import sys
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
from google.cloud import bigquery

app = Flask(__name__)
socketio = SocketIO(app, ping_timeout=20, ping_interval=10)

# CLI 인자로 가로 및 세로 길이를 입력받아 면적 계산
if len(sys.argv) != 3:
    print("Usage: python app.py <width> <height>")
    sys.exit(1)

width = float(sys.argv[1])
height = float(sys.argv[2])
area = width * height

# GCS 설정
PROJECT_ID = "YOURPROJECTID"  # 프로젝트 ID
BUCKET_NAME = "YOURBUCKETNAME"  # 버킷 이름
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

# Google Cloud Platform settings
ENDPOINT_ID = "YOURENDPOINTID"
LOCATION = "YOURLOCATION"
DATASET_ID = "YOUTDATASETID"
TABLE_ID = "YOURTABLEID"

# Vertex AI 및 BigQuery 초기화
project_id = PROJECT_ID
location = LOCATION
vertexai.init(project=project_id, location=location)
bq_client = bigquery.Client()


# Gemini 모델 설정
model = GenerativeModel("gemini-1.5-pro-001")
generation_config = {
    "max_output_tokens": 300,
    "temperature": 0.7,
    "top_p": 0.9,
}
safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
]

def generate_query(user_input):
    dataset_info = """
    The dataset is named 'YOURBIGQUERYDATASET' and has the following columns:
    - 행: (INTEGER) a row number
    - number: (INTEGER) a unique identifier
    - timestamp: (TIMESTAMP) the time of the event, formatted as '2024-08-01 00:00:16 UTC'
    - person_count: (INTEGER) the count of people present at the time
    
    Requirements:
    1. You must never generate a query that adds, modifies, or deletes data.
    2. If the user input contains relative date expressions such as 'yesterday' or 'last week', you must calculate these based on today's date.

    Based on the user input, generate an SQL query that fetches the required data from this table.
    Always include both the 'timestamp' and 'person_count' fields in the SELECT clause of the query.
    If aggregating data, use aliases to ensure the result contains both 'timestamp' and 'person_count' (or similarly named count field).
    For minimum or maximum counts, select a corresponding timestamp as well.
    """

    # 현재 날짜를 기준으로 상대적인 날짜 계산
    full_prompt = dataset_info + f"\n\nToday's date is {datetime.now().date()}.\n\nUser input: {user_input}\nGenerate an SQL query to answer this question:"
    
    response = model.generate_content(
        [full_prompt],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False,
    )
    
    query = response.text.strip()
    query = query.replace("```sql", "").replace("```", "").strip()
    
    if any(keyword in query.lower() for keyword in ["insert", "delete", "update", "drop", "alter"]):
        raise ValueError("The generated query attempts to modify the database, which is not allowed.")
    
    if "timestamp" not in query or ("person_count" not in query and "count" not in query.lower()):
        raise ValueError("The generated query does not include required fields.")
    
    return query

def query_bigquery(query):
    query_job = bq_client.query(query)
    return query_job.result()

def generate_natural_language_response(results):
    if not results.total_rows:
        return "No data available for the specified query."
    
    rows = []
    for row in results:
        row_dict = dict(row.items())
        rows.append(row_dict)
    
    prompt = f"Convert the following SQL query results into a Korean natural language summary:\n\n{rows}"
    response = model.generate_content(
        [prompt],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False,
    )
    
    return response.text.strip()



# 전역 변수
cached_frame = None
frame_lock = threading.Lock()

def determine_color_based_on_density(person_count, area):
    density = person_count / area
    if density <= 3.5:
        return (0, 255, 0)  # Green (Safe)
    elif density <= 4:
        return (255, 255, 0)  # Yellow (Caution)
    elif density <= 5:
        return (255, 0, 0)  # Blue (Warning)
    else:
        return (0, 0, 255)  # Red (Danger)

def predict_image_object_detection_sample(image):
    client_options = {"api_endpoint": f"{LOCATION}-aiplatform.googleapis.com"}
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    endpoint = client.endpoint_path(project=PROJECT_ID, location=LOCATION, endpoint=ENDPOINT_ID)

    _, buffer = cv2.imencode('.jpg', image)
    encoded_content = base64.b64encode(buffer).decode("utf-8")

    instance = predict.instance.ImageObjectDetectionPredictionInstance(content=encoded_content).to_value()
    instances = [instance]
    parameters = predict.params.ImageObjectDetectionPredictionParams(confidence_threshold=0.5).to_value()

    response = client.predict(endpoint=endpoint, instances=instances, parameters=parameters)
    return response.predictions

def insert_into_bigquery(timestamp, person_count):
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = client.dataset(DATASET_ID).table(TABLE_ID)
    table = client.get_table(table_ref)

    rows_to_insert = [
        {"number": 1, "timestamp": timestamp, "person_count": person_count}
    ]

    errors = client.insert_rows_json(table, rows_to_insert)
    if errors:
        print(f"Encountered errors while inserting rows: {errors}")
    else:
        print(f"Inserted {len(rows_to_insert)} rows into {DATASET_ID}.{TABLE_ID}.")

def fetch_latest_image():
    global cached_frame
    while True:
        # GCS에서 가장 최근에 업로드된 이미지 찾기
        blobs = list(bucket.list_blobs(prefix="img/"))
        if not blobs:
            print("No images found in the bucket.")
            time.sleep(1)  # 이미지가 없으면 1초 후 다시 시도
            continue

        # 가장 최근의 blob 찾기 blob: GCS bucket 메타데이터
        latest_blob = max(blobs, key=lambda b: b.time_created)
        print(f"Fetching image: {latest_blob.name} uploaded at {latest_blob.time_created}")

        image_bytes = latest_blob.download_as_bytes()

        # 이미지 디코딩
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            print("Error: Failed to decode image.")
            time.sleep(1)
            continue

        # AI 예측 수행
        predictions = predict_image_object_detection_sample(frame)
        person_count = len(predictions[0]['bboxes']) if predictions else 0

        # 밀도 기반 색상 결정
        bg_color = determine_color_based_on_density(person_count, area)

        # 이미지 후처리 (예: Gaussian Blur 및 텍스트 추가)
        blurred_frame = cv2.GaussianBlur(frame, (15, 15), 0)
        text = f"Persons: {person_count}, Area: {area} m^2"
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        center_x = blurred_frame.shape[1] // 2
        center_y = 50

        cv2.rectangle(blurred_frame, (center_x - text_width // 2 - 10, center_y - text_height // 2 - 10),
                      (center_x + text_width // 2 + 10, center_y + text_height // 2 + 10), bg_color, -1)
        cv2.putText(blurred_frame, text, (center_x - text_width // 2, center_y + text_height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        with frame_lock:
            cached_frame = blurred_frame

        print("Frame cached successfully.")

        # BigQuery에 결과 저장
        timestamp = datetime.now(timezone(timedelta(hours=9))).isoformat()
        insert_into_bigquery(timestamp, person_count)  # number 필드는 카메라 1번 즉 고정된 1로 사용 (서비스 확대시 카메라 고유번호 사용)

        time.sleep(1)  # 1초마다 업데이트 (1초에 1프레임)

def serve_cached_frames():
    global cached_frame
    while True:
        if cached_frame is not None:
            with frame_lock:
                _, buffer = cv2.imencode('.jpg', cached_frame)
                frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            print("Serving cached frame.")
        else:
            print("No cached frame available.")
        time.sleep(1)  # 1초에 1프레임 스트리밍

@app.route('/video_feed')
def video_feed():
    return Response(serve_cached_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/live-view')
def live_view():
    return render_template('live-view.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def help_page():
    return render_template('chat.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get('question')
    
    try:
        query = generate_query(user_input)
        results = query_bigquery(query)
        response_text = generate_natural_language_response(results)
        return jsonify({'response': response_text})
    
    except ValueError as e:
        return jsonify({'error': f"Error in query generation: {str(e)}"})
    except Exception as e:
        return jsonify({'error': f"Unexpected error occurred: {str(e)}"})


@app.route('/recent-records')
def recent_records():
    return render_template('recent-records.html')

if __name__ == '__main__':
    # 주기적으로 GCS에서 최신 이미지 가져오는 스레드 시작
    threading.Thread(target=fetch_latest_image, daemon=True).start()

    # Flask 애플리케이션 실행
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
