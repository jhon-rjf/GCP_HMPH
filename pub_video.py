import time
import base64
import cv2
from google.cloud import pubsub_v1
topic_id='projects/andong-24-team-102/topics/test'

class Video_processor:
  def __init__(self, video_path) -> None:
    try:
      self.capture=cv2.VideoCapture(video_path)
      self.capture.isOpened()
    except FileNotFoundError :
      raise FileNotFoundError("File isn't found, please check file path") 
    except IsADirectoryError:
      raise IsADirectoryError("This please enter a file path")
    except  PermissionError :
      raise PermissionError("Don't have permission to read this file")

  def _check_video_path(self) -> None:
    incorrect_path=not self.capture.isOpened()

    if incorrect_path:
      print('error: cloud not open video\n')
      exit()

  def encode_current_frame(self) -> None:
    ret, img_nparr=self.capture.read()
    imread_flase=not ret

    if imread_flase:
      self.video_restart()
      ret, img_nparr=self.capture.read()

    _, img=cv2.imencode('.png', img_nparr)
    img_byte=img.tobytes()
    encoded_img=base64.b64encode(img_byte)
    return encoded_img
  
  def skip_video_per_sec(self, skip_time_sec) -> None:
    skip_time_msec=skip_time_sec*1000
    current_position=cv2.CAP_PROP_POS_MSEC
    current_position_msec=self.capture.get(current_position)
    next_position=current_position_msec+skip_time_msec
    self.capture.set(current_position, next_position)
    self.check_video_overrun(next_position)

  def check_video_overrun(self, next_position) -> None:
    total_frames=int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps=self.capture.get(cv2.CAP_PROP_FPS)
    video_length_msec=(total_frames/fps)*1000
    video_overrun=video_length_msec<next_position

    if video_overrun:
      self.video_restart()

  def video_restart(self):
    self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

class Publisher:
  def __init__(self, topic_id) -> None: 
    self.publisher=pubsub_v1.PublisherClient()
    self.topic_path=topic_id

  def publish(self, product) -> None:
    future=self.publisher.publish(self.topic_path, product)
    self.check_publsih(future)

  def check_publsih(future) -> None:
    try:
      future.result()  
      print("Published message to topic.")
    except Exception as e:
      print(f"Failed to publish message: {e}")

path_error=(FileNotFoundError, IsADirectoryError)

while True:
  try:
    video_path=input('please input path of video file: ')
    processor=Video_processor(video_path)
  except path_error:
    pass
  except PermissionError:
    pass
  else:
    break

pub=Publisher(topic_id)

while True:
  encoded_img=processor.encode_current_frame()
  pub.publish(encoded_img)
  time.sleep(1)
  processor.skip_video_per_sec(1)
