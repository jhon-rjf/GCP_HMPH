import base64
import numpy as np
from PIL import Image
import io
import cv2
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from google.cloud import storage

def decode_base64(base64_str):
  bin_img = base64.b64decode(base64_str)
  img = Image.open(io.BytesIO(bin_img))
  img = np.array(img)
  return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

class Saving_img_to_gcs(beam.DoFn):
  def __init__(self, bucket_name):
    self.image_number=0
    self.bucket_name=bucket_name

  def process(self,np_arr_img):
    storage_client=storage.Client()  #process로 옮기면 피클링 안함
    bucket=storage_client.bucket(self.bucket_name)
    file_path=f'img/image_{self.image_number}.png'
    blob=bucket.blob(f'{file_path}')
    self.image_number+=1

    if self.image_number==1800:
      self.image_number=0

    _,buffer_img=cv2.imencode('.png',np_arr_img)
    blob.upload_from_string(buffer_img.tobytes(),content_type='image/png')

topics='projects/andong-24-team-102/topics/test'
bucket_name='mypipestorage'

pipeline_options = PipelineOptions(
  project='andong-24-team-102',     
  runner='DataflowRunner',
  temp_location='gs://mypipestorage/temp',
  region='us-central1',
  max_num_workers=10,
  save_main_session=True,
  environment_config='gs://mypipestorage/Docker.Dockerfile',
  output='gs://mypipestorage/output'
  )

def run():
  with beam.Pipeline(options=pipeline_options) as p:
    input = p | 'Read' >> beam.io.ReadFromPubSub(topic=topics)
    decode_img = input | 'Decode' >> beam.Map(decode_base64) 
    decode_img| 'save' >> beam.ParDo(Saving_img_to_gcs(bucket_name))

if __name__ == '__main__':
    run()
