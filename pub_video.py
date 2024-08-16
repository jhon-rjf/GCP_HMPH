import time
import base64
import cv2
from google.cloud import pubsub_v1

class Video_processor:
  def __init__(self) -> None:
    self.video_path=input('please input path of video file: ')
    self.capture=cv2.VideoCapture(self.video_path)
    self._check_video_path()
    self.video_length=self._get_video_length()

  def encode_current_frame(self) -> None:
    _, img_nparr=self.capture.read()
    _, img=cv2.imencode('.png', img_nparr)
    img_byte=img.tobytes()
    encoded_img=base64.b64encode(img_byte)
    return encoded_img
  
  def skip_video_per_sec(self, skip_time_sec) -> None:
    skip_time_msec=skip_time_sec*1000
    current_position_msec=self.capture.get(cv2.CAP_PROP_POS_MSEC)
    next_position=current_position_msec+skip_time_msec
    is_overrun=next_position>self.video_length

    if is_overrun:
      self._video_restart()
    else:
      self.capture.set(cv2.CAP_PROP_POS_MSEC, next_position)

  def _video_restart(self):
    self.capture.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)

  def _get_video_length(self):
    self.capture.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
    video_length=self.capture.get(cv2.CAP_PROP_POS_MSEC)
    self.capture.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)
    return video_length

  def _check_video_path(self) -> None:
    correct_path = self.capture.isOpened()

    while not correct_path:
      self.capture.release()    
      print("Please check file path")
      self.video_path=input('Please input path of video file: ')
      self.capture=cv2.VideoCapture(self.video_path)
      correct_path = self.capture.isOpened()

class Ppublisher:
  def __init__(self, topic_id) -> None: 
    self.publisher=pubsub_v1.PublisherClient()
    self.topic_path=topic_id

  def publish(self, product) -> None:
    future=self.publisher.publish(self.topic_path, product)
    
    try:
      future.result()
    except Exception as e:    #기본 재시도 로직 실패시 종료
      print(f"Failed to publish: {e}")
      exit()

def main():
  topic_id='projects/andong-24-team-102/topics/test'
  processor=Video_processor()
  pub=Ppublisher(topic_id)

  while True:
    encoded_img=processor.encode_current_frame()
    pub.publish(encoded_img)
    time.sleep(1)
    processor.skip_video_per_sec(1)

if __name__=='__main__':
  main()
