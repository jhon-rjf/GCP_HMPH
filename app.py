from flask import Flask, render_template, Response, jsonify
from ultralytics import YOLO
import cv2
import numpy as np
from collections import defaultdict
import serial
import time

app = Flask(__name__)

# YOLO 모델 로드
model = YOLO('/Users/jeong-yungeol/yolov8_test/yolov8n.pt')

# 전역 변수
camera = None
arduino = None
current_count = 0
previous_led_state = None  # LED 상태 추적을 위한 변수 추가

def setup_arduino():
    global arduino
    try:
        arduino = serial.Serial('/dev/cu.usbmodem101', 9600, timeout=1)
        time.sleep(2)
    except Exception as e:
        print(f"Arduino connection failed: {e}")
        arduino = None

def get_led_state(count):
    """인원수에 따른 LED 상태 반환"""
    if count <= 3:
        return 'G'
    elif count == 4:
        return 'Y'
    else:
        return 'R'

def control_leds(count):
    """LED 상태가 변경될 때만 제어 신호 전송"""
    global previous_led_state
    
    if arduino is None:
        return
        
    try:
        current_state = get_led_state(count)
        
        # LED 상태가 변경되었을 때만 신호 전송
        if current_state != previous_led_state:
            arduino.write(current_state.encode())
            previous_led_state = current_state
            print(f"LED state changed to: {current_state}")  # 디버깅용
            
    except Exception as e:
        print(f"Error controlling LEDs: {e}")

def get_warning_level(count):
    if count <= 3:
        return {"level": "양호", "color": "#28a745"}  # 녹색
    elif count == 4:
        return {"level": "주의", "color": "#ffc107"}  # 노란색
    else:
        return {"level": "경고", "color": "#dc3545"}  # 빨간색

def get_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return camera

def apply_gaussian_blur(frame, box):
    x1, y1, x2, y2 = map(int, box)
    # 박스 영역 추출
    roi = frame[y1:y2, x1:x2]
    # 가우시안 블러 적용
    blurred_roi = cv2.GaussianBlur(roi, (45, 45), 30)
    # 블러 처리된 영역을 원본 이미지에 다시 삽입
    frame[y1:y2, x1:x2] = blurred_roi
    return frame

def calculate_iou(box1, box2):
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2
    
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    if x2_i < x1_i or y2_i < y1_i:
        return 0.0
    
    intersection_area = (x2_i - x1_i) * (y2_i - y1_i)
    box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
    box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
    
    iou = intersection_area / float(box1_area + box2_area - intersection_area)
    return iou

def track_objects(previous_boxes, current_boxes, iou_threshold=0.5):
    if not previous_boxes:
        return {i: i for i in range(len(current_boxes))}
    
    iou_matrix = np.zeros((len(previous_boxes), len(current_boxes)))
    for i, prev_box in enumerate(previous_boxes):
        for j, curr_box in enumerate(current_boxes):
            iou_matrix[i, j] = calculate_iou(prev_box, curr_box)
    
    matched_indices = {}
    for i in range(len(previous_boxes)):
        if np.max(iou_matrix[i]) > iou_threshold:
            matched_idx = np.argmax(iou_matrix[i])
            matched_indices[matched_idx] = i
    
    current_max_id = max(matched_indices.values()) if matched_indices else -1
    for i in range(len(current_boxes)):
        if i not in matched_indices:
            current_max_id += 1
            matched_indices[i] = current_max_id
            
    return matched_indices

def generate_frames():
    previous_boxes = []
    camera = get_camera()
    global current_count
    
    # 프레임 처리 속도 제어를 위한 변수
    last_led_update = time.time()
    led_update_interval = 0.5  # LED 업데이트 간격 (초)
    
    while True:
        success, frame = camera.read()
        if not success:
            break
            
        try:
            results = model(frame)
            current_boxes = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    if int(box.cls) == 0:  # 사람만 감지
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        current_boxes.append([x1, y1, x2, y2])
            
            current_count = len(current_boxes)
            
            # LED 업데이트 간격 체크
            current_time = time.time()
            if current_time - last_led_update >= led_update_interval:
                control_leds(current_count)
                last_led_update = current_time
            
            if current_boxes:
                tracked_objects = track_objects(previous_boxes, current_boxes)
                
                for i, box in enumerate(current_boxes):
                    x1, y1, x2, y2 = box
                    track_id = tracked_objects[i]
                    
                    # 바운딩 박스 그리기
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # ID 표시
                    cv2.putText(frame, f'ID: {track_id}', (x1, y1-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    # 가우시안 블러 적용
                    frame = apply_gaussian_blur(frame, box)
                
                # 전체 인원수 표시
                cv2.putText(frame, f'Total Persons: {current_count}', (20, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                previous_boxes = current_boxes.copy()
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                   
        except Exception as e:
            print(f"Error in generate_frames: {e}")
            continue

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_count')
def get_count():
    warning_info = get_warning_level(current_count)
    return jsonify({
        'count': current_count,
        'warning_level': warning_info['level'],
        'warning_color': warning_info['color']
    })

def cleanup():
    global camera, arduino
    if camera is not None:
        camera.release()
    if arduino is not None:
        arduino.close()

if __name__ == '__main__':
    try:
        setup_arduino()  # 아두이노 초기 설정
        app.run(debug=True, host='0.0.0.0', port=5002)
    finally:
        cleanup()
