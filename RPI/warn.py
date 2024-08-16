import time
import os
import RPi.GPIO as GPIO
from google.cloud import bigquery

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcloud-team-project-credential-key.json'

class LED_controler:
  def __init__(self, *led_pins):
    self.led_pins=led_pins

    for led in self.led_pins:
      GPIO.setup(led, GPIO.OUT)

  def on(self,*led_pins):
    leds=led_pins if led_pins else self.led_pins
    for led in leds:
        GPIO.output(led, True)
    
  def off(self,*led_pins):
    leds=led_pins if led_pins else self.led_pins
    for led in leds:
      GPIO.output(led, False)
  
"""   
  def warning(self):
    for led in self.led_pins:
      self.on(led)
      time.sleep(0.15)
      self.off(led)
      time.sleep(0.15)
 """

class Buzzer_controler:
  def __init__(self, *buzzer_pins):
    self.buzzer_pins=buzzer_pins

    for buzzer in buzzer_pins:
      GPIO.setup(buzzer, GPIO.OUT)
    
  def on(self, *buzzer_pins):
    buzzers=buzzer_pins if buzzer_pins else self.buzzer_pins

  def off(self, *buzzer_pins):
    buzzers=buzzer_pins if buzzer_pins else self.buzzer_pins
    
class Warner:
  def __init__(self,*warners) -> None:
    warners=warners()

def main():
  GPIO.setmode(GPIO.BCM)
  led_pins=14,15
  buzzer=13

  led=LED_controler(led_pins)
  buzzer=Buzzer_controler(buzzer)

    

  def __del__():
    GPIO.cleanup()


#   client=bigquery.Client()

#   query=""" 
#     SLECT [num of human]
#     FROM andong-24-team-102.vm_to_bq.[table]

#   """

#   query_job=client.query(query)
#   result=query_job.result()

if __name__=='__main__':
  main()
