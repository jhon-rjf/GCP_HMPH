#반드시 설치할 것
#!pip3 insall apache_beam
#!pip3 install apache_baeam[gcp]
#!pip3 install opencv-python
#!pip3 install numpy
#!pip3 install pillow
#!gcloud services disable dataflow.googleapis.com --force
#!gcloud services enable dataflow.googleapis.com
#requirement_file

import base64
import numpy as np
from PIL import Image
import io
import cv2
import apache_beam as beam
from apache_beam.options.pipeline_options import _BeamArgumentParser, PipelineOptions
from google.cloud import storage

def decode_base64(base64_str):
  bin_img = base64.b64decode(base64_str)
  img = Image.open(io.BytesIO(bin_img))
  img = np.array(img)
  return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

class saving_img_to_gcs(beam.DoFn):
  def __init__(self, bucket_name):
    self.index=0
    self.bucket_name=bucket_name

  def process(self,np_arr_img):
    storage_client=storage.Client()  #process로 옮기면 피클링 안함?
    bucket=storage_client.bucket(self.bucket_name)
    filename=f'image_{self.index}.png'
    blob=bucket.blob(f'{filename}')
    self.index+=1
    _,buffer_img=cv2.imencode('.png',np_arr_img)
    blob.upload_from_string(buffer_img.tobytes(),content_type='image/png')

pipeline_options = PipelineOptions(
  project='andong-24-adv-idv-108',     #프로젝트 id 입력
  runner='DataflowRunner',
  temp_location='gs://marginzoa/temp',    
  staging_location='gs://marginzoa/staging',    #지역 설정할것
  region='us-central1',    #위치 설정
  max_num_workers=10,
  save_main_session=True,
  setup_file='./setup.py'
  # requirements_file='./Requirements.txt'
  )
  

topics='projects/andong-24-adv-idv-108/topics/test'           #토픽 경로 입력
bucket_name='gs://marginzoa'

def run():
  with beam.Pipeline(options=pipeline_options) as p:
    input = p | 'Read' >> beam.io.ReadFromPubSub(topic=topics)
    decode_img = input | 'Decode' >> beam.Map(decode_base64) 
    #test
    decode_img| 'save' >> beam.ParDo(saving_img_to_gcs(bucket_name))

# 파이프라인 실행
if __name__ == '__main__':
    run()