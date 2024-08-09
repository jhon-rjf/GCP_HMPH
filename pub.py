import base64
import cv2
from google.cloud import pubsub_v1

class video_processor:
  def __init__(self, video_path) -> None:
    self.capture=cv2.VideoCapture(video_path)
    self.check_video_path()

  def check_video_path(self) -> None:
    incorrect_path=not(self.capture.isOpened())

    if(incorrect_path):
      print('error: cloud not open video')
      exit()

  def encode_current_frame(self):
    _,img=self.capture.read()
    encoded_img=base64.b64decode(img)
    return encoded_img
  
  def skip_video_per_sec(self, skip_time_msec) -> None:
    skip_time_sec=skip_time_msec*1000
    current_position=cv2.CAP_PROP_POS_MSEC
    current_position_msec=self.capture.get(current_position)
    next_position=current_position_msec+skip_time_sec
    self.capture.set(current_position, next_position)

class publisher:
  def __init__(self, project, topic, certificate_key) -> None: 
    self.publisher=pubsub_v1.PublisherClient()
    self.topic_path=publisher.topic_path(project, topic)

    

  def publish(self, product) -> None:
    publisher.publish(self.topic_path, product)

video_path=input('please input path of video file: ')
project='andong-24-team-102'
topic='projects/andong-24-team-102/topics/test'

processor=video_processor()
pub=publisher(project, topic)

while True:
  encoded_img=processor.encode_current_frame()
  pub.publish(encoded_img)
  processor.skip_video_per_sec(1)
