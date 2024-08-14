import os
import time
import base64
import cv2
from picamera2 import Picamera2
from google.cloud import pubsub_v1

# 환경 변수 설정
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcloud-team-project-credential-key.json'

class VideoProcessor:
    def __init__(self):
        self.picamera2 = Picamera2()
        self.picamera2.start_preview()
        time.sleep(2)  
        self.picamera2.start()

    def capture_frame(self):
        # 프레임 캡처
        img_nparray = self.picamera2.capture_array()
        return img_nparray

    def encode_current_frame(self):
        img_nparray = self.capture_frame()
        
        _, img_base64 = cv2.imencode('.png', img_nparray)
        img_byte = img_base64.tobytes() 
        encoded_img = base64.b64encode(img_byte)
        return encoded_img

class Publisher:
    def __init__(self, topic_id):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = topic_id

    def publish(self, product):
        future = self.publisher.publish(self.topic_path, product)
        try:
            future.result()  # 메시지가 성공적으로 발행되었는지 확인
            print("Published message to topic.")
        except Exception as e:
            print(f"Failed to publish message: {e}")

def main():
    topic_id = 'projects/andong-24-team-102/topics/test'

    processor = VideoProcessor()
    pub = Publisher(topic_id)

    try:
        while True:
            encoded_img = processor.encode_current_frame()
            pub.publish(encoded_img)
            time.sleep(1)  # 1초 대기
    except KeyboardInterrupt:
        print("Process interrupted.")
    finally:
        processor.picamera2.close()  

if __name__ == "__main__":
    main()
