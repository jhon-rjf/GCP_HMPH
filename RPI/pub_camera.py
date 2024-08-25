import json
import os
import time
import base64
import cv2
from picamera2 import Picamera2
from google.cloud import pubsub_v1

class Camera:
  def __init__(self) -> None:
    self.__camera=Picamera2()
    self.__camera_start()
  
  def __camera_start(self) -> None:
    self.__camera.start_preview()
    time.sleep(2)
    self.__camera.start()

  def capture_frame(self) -> list[int]:
    img_array=self.__camera.capture_array()
    return img_array

  def __del__(self) -> None:
    self.__camera.close()

class VideoProcessor:
  def __init__(self) -> None:
    self.__frame

  def get_frame(self, frame) -> None:
    self.__frame=frame

  def encode_frame(self) -> str:
    img_array = self.__frame
    _, img_base64 = cv2.imencode('.png', img_array)
    img_byte = img_base64.tobytes()
    encoded_img = base64.b64encode(img_byte)
    return encoded_img

class Publisher:
  def __init__(self, topic_id) -> None:
    self.__publisher = pubsub_v1.PublisherClient()
    self.__topic_path = topic_id

  def publish(self, product) -> None:
    future = self.__publisher.publish(self.__topic_path, product)
    try:
      future.result() 
    except Exception as e:
      print(f"Failed to publish: {e}")#테스트용

def main() -> None:
  setting_file_path=os.path.join('settings','pub_settings.json')
  try:
    with open(setting_file_path, 'r', encoding='utf-8') as file:
      file_data=json.load(file)
      topic_id=file_data['topic_id']
      credential_path=file_data['credential_path']
  except FileNotFoundError as e:
    print(f'File not found: {e}')
    print(f'Error message: {e}')
    exit()
  except json.JSONDecodeError as e:
    print(f'Error decoding json {e}')
    print(f'Error message: {e}')
    exit()

  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

  camera = Camera()
  processor = VideoProcessor()
  pub = Publisher(topic_id)

  try:
    while True:
      frame=camera.capture_frame()
      processor.get_frame(frame)
      encoded_img = processor.encode_frame()
      pub.publish(encoded_img)
      time.sleep(1)
  finally:
    processor.picamera2.close()  

if __name__=='__main__':
  main()
