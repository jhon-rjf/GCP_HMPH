#반드시 설치할 것
#pip insall apache_beam
#pip install apache_baeam[gcp]

import base64
import numpy as np
from PIL import Image
import io
import cv2
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions


pubsub=''           #토픽 경로 입력
#subscription

def decode_base64(base64_str):
    bin_img = base64.b64decode(base64_str)
    img = Image.open(io.BytesIO(bin_img))
    img = np.array(img)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def downscale(img):
   pass
    

pipeline_options = PipelineOptions(
    project='',     #프로젝트 id 입력
    runner='DataflowRunner',
    temp_location='',   #지역 설정할것 
    region=''     #위치 설정
)

def run():
    with beam.Pipeline(options=pipeline_options) as p:
        (p
        | 'Read' >> beam.io.ReadFromPubSub(pubsub)        
        | 'decode' >> decode_base64() 
        | 'Write' >> beam.io.WriteToText(''))

# 파이프라인 실행
if __name__ == '__main__':
    run()