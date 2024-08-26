import os
import json
import time
import base64
import cv2
from google.cloud import pubsub_v1

class VideoProcessor:
  def __init__(self, video_path) -> None:
    self.__video_path=video_path
    self.__capture=cv2.VideoCapture(self.__video_path)
    self.__check_video_path()
    self.__video_length=self.__get_video_length()

  def encode_current_frame(self) -> None:
    _, img_array=self.__capture.read()
    _, img=cv2.imencode('.png', img_array)
    img_byte=img.tobytes()
    encoded_img=base64.b64encode(img_byte)
    return encoded_img
  
  def skip_video_per_sec(self, skip_time_sec) -> None:
    skip_time_msec=skip_time_sec*1000
    current_position_msec=self.__capture.get(cv2.CAP_PROP_POS_MSEC)
    next_position=current_position_msec+skip_time_msec
    video_length_msec=self.__video_length*1000
    self.__check_overrun(next_position, video_length_msec)
    
  def __check_overrun(self, next_position, video_length_msec) -> None:
    is_overrun=next_position>video_length_msec

    if is_overrun:
      self.__video_restart()
    else:
      self.__capture.set(cv2.CAP_PROP_POS_MSEC, next_position)


  def __video_restart(self) -> None:
    self.__capture.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)

  def __get_video_length(self) -> int:
    total_frame=int(self.__capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps=int(self.__capture.get(cv2.CAP_PROP_FPS))
    video_length=int(total_frame/fps)-1
    return video_length

  def __check_video_path(self) -> None:
    correct_path = self.__capture.isOpened()

    while not correct_path:
      self.__capture.release()
      self.__video_path=input('Please input path of video file: ')
      self.__capture=cv2.VideoCapture(self.__video_path)
      correct_path = self.__capture.isOpened()

  def __del__(self) -> None:
    self.__capture.release()

class Publisher:
  def __init__(self, topic_id) -> None: 
    self.__publisher=pubsub_v1.PublisherClient()
    self.__topic_path=topic_id

  def publish(self, product) -> None:
    future=self.__publisher.publish(self.__topic_path, product)
    
    try:
      future.result()
    except Exception as e:    
      print(f"Failed to publish: {e}")
      exit()

def main() -> None:
  setting_file_path=os.path.join('settings','pub_settings.json')
  settings_file_data=open_file(setting_file_path)
  topic_id=settings_file_data['topic_id']
  credential_path=settings_file_data['credential_path']
  video_path=settings_file_data['video_path']
  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

  processor=VideoProcessor(video_path)
  publisher=Publisher(topic_id)

  while True:
    encoded_img=processor.encode_current_frame()
    publisher.publish(encoded_img)
    time.sleep(1)
    processor.skip_video_per_sec(1)

def open_file(file_path):
  try:
    with open(file_path, 'r', encoding='utf-8') as file:
      file_data=json.load(file)
      return file_data
  except FileNotFoundError as e:
    print(f'File not found: {e}')
    print(f'Error message: {e}')
    exit()
  except json.JSONDecodeError as e:
    print(f'Error decoding json {e}')
    print(f'Error message: {e}')
    exit()

if __name__=='__main__':
  main()
