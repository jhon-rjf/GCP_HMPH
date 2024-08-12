import time
import base64
import cv2
from google.cloud import pubsub_v1

class video_processor:
  def __init__(self, video_path) -> None:
    self.capture=cv2.VideoCapture(video_path)
    self._check_video_path()

  def _check_video_path(self) -> None:
    incorrect_path=not self.capture.isOpened()

    if(incorrect_path):
      print('error: cloud not open video\n')
      exit()

  def encode_current_frame(self):
    ret, img_nparr=self.capture.read()
    imread_flase=not ret
    # print(ret)

    if imread_flase:
      self.video_restart()
      ret, img_nparr=self.capture.read()

    img_byte=cv2.imencode('.jpg', img_nparr)[1].tobytes()
    encoded_img=base64.b64encode(img_byte)
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
      self.video_restart()

  def video_restart(self):
    self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

class publisher:
  def __init__(self, topic_id) -> None: 
    self.publisher=pubsub_v1.PublisherClient()
    self.topic_path=topic_id

  def publish(self, product) -> None:
    future=self.publisher.publish(self.topic_path, product)
    try:
      future.result()  # 메시지가 성공적으로 발행되었는지 확인
      print("Published message to topic.")
    except Exception as e:
      print(f"Failed to publish message: {e}")

video_path=input('please input path of video file: ')
topic_id='projects/andong-24-team-102/topics/test'

processor=video_processor(video_path)
pub=publisher(topic_id)

while True:
  encoded_img=processor.encode_current_frame()
  pub.publish(encoded_img)
  time.sleep(1)
  processor.skip_video_per_sec(1)
