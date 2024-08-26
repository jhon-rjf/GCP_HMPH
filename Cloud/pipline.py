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
    storage_client=storage.Client()  #process로 옮기면 피클링 안함
    bucket=storage_client.bucket(self.bucket_name)
    file_path=f'img/image_{self.index}.png'
    blob=bucket.blob(file_path)
    self.index+=1
    _,buffer_img=cv2.imencode('.png',np_arr_img)
    blob.upload_from_string(buffer_img.tobytes(),content_type='image/png')

topics='projects/andong-24-team-102/topics/test'           #토픽 경로 입력
bucket_name='mypipestorage'

pipeline_options = PipelineOptions(
  project='andong-24-team-102',     #프로젝트 id 입력
  runner='DataflowRunner',
  temp_location='gs://mypipestorage/temp',    
  staging_location='gs://mypipestorage/staging',    #지역 설정할것
  region='us-central1',    #위치 설정
  max_num_workers=10,
  save_main_session=True,
  setup_file='./setup.py'
  )

def run():
  with beam.Pipeline(options=pipeline_options) as p:
    input = p | 'Read' >> beam.io.ReadFromPubSub(topic=topics)
    decode_img = input | 'Decode' >> beam.Map(decode_base64) 
    decode_img| 'save' >> beam.ParDo(saving_img_to_gcs(bucket_name))

# 파이프라인 실행
if __name__ == '__main__':
    run()
