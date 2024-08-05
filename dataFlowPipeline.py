#반드시 설치할 것
#!pip3 insall apache_beam
#!pip3 install apache_baeam[gcp]
#!pip3 install opencv-python
#!pip3 install numpy
#!pip3 install pillow
#!gcloud services disable dataflow.googleapis.com --force
#!gcloud services enable dataflow.googleapis.com

import base64
import numpy as np
from PIL import Image
import io
import cv2
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from google.cloud import storage

topics='projects/andong-24-adv-idv-108/topics/test'           #토픽 경로 입력
bucket_name='gs://marginzoa'
#subscription

def decode_base64(base64_str):
  bin_img = base64.b64decode(base64_str)
  img = Image.open(io.BytesIO(bin_img))
  img = np.array(img)
  return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

class saving_img_to_gcs(beam.DoFn):
  def __init__(self, bucket_name):
    storage_client=storage.Client()
    self.bucket=storage_client.bucket(bucket_name)
    self.index=0

  def process(self,np_arr_img):
    filename=f'image_{self.index}.png'
    blob=self.bucket.blob(f'img/{filename}')
    self.index+=1
    _,buffer_img=cv2.imencode('.png',np_arr_img)
    blob.upload_from_string(buffer_img.tobytes(),content_type='image/png')
    
    

pipeline_options = PipelineOptions(
  project='andong-24-adv-idv-108',     #프로젝트 id 입력
  runner='DataflowRunner',
  temp_location='gs://marginzoa/temp',   #지역 설정할것 
  staging_location='gs://marginzoa/staging',
  region='us-central1',    #위치 설정
  max_num_workers=10)

def run():
  with beam.Pipeline(options=pipeline_options) as p:
    input = p | 'Read' >> beam.io.ReadFromPubSub(topic=topics)
    decode_img = input | 'Decode' >> beam.Map(decode_base64) 
    #test
    decode_img| 'save' >> beam.ParDo(saving_img_to_gcs(bucket_name))

# 파이프라인 실행
if __name__ == '__main__':
    run()