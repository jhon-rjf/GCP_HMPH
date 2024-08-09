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
    encoded_img=base64.b64encode(img)
    return encoded_img
  
  def skip_video_per_sec(self, skip_time_sec) -> None:
    skip_time_msec=skip_time_sec*1000
    current_position=cv2.CAP_PROP_POS_MSEC
    current_position_msec=self.capture.get(current_position)
    next_position=current_position_msec+skip_time_msec
    self.capture.set(current_position, next_position)
    self.check_video_overrun(next_position)
  
  def check_video_overrun(self, next_position):
    total_frames=int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps=self.capture.get(cv2.CAP_PROP_FPS)
    video_length_msec=(total_frames/fps)*1000
    
    if (video_length_msec<next_position):
      self.capture.set()

class publisher:
  def __init__(self, project, topic) -> None: 
    self.publisher=pubsub_v1.PublisherClient()
    self.topic_path=publisher.topic_path(project, topic)

  def publish(self, product) -> None:
    self.publisher.publish(self.topic_path, product)

video_path=input('please input path of video file: ')
project='andong-24-team-102'
topic='projects/andong-24-team-102/topics/test'

processor=video_processor()
pub=publisher(project, topic)

while True:
  encoded_img=processor.encode_current_frame()
  pub.publish(encoded_img)
  processor.skip_video_per_sec(1)
