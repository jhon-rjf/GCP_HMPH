import base64
from google.cloud import pubsub_v1

project='andong-24-team-102'
topic='projects/andong-24-team-102/topics/test'

text='이미지 경로를 입력하세요: '
text=text.encode('utf-8')

img_path=input(text)

with open(img_path, 'r') as img:
  global encoded_img
  encoded_img=base64.b64encode(img)

while(1):
  publisher=pubsub_v1.PublisherClient()
  topic_path=publisher.topic_path(project, topic)
  publisher.publish(topic_path, encoded_img)
