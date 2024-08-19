import time
import os
import RPi.GPIO as GPIO
from abc import ABC, abstractmethod
from google.cloud import bigquery
import itertools

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcloud-team-project-credential-key.json'

class Alarm_unit(ABC):
  def __init__(self, *pins:int):

    for unit in pins:
      GPIO.setup(unit, GPIO.OUT)

  @abstractmethod
  def alert(self):
    pass

class LED(Alarm_unit):
  def __init__(self, *led_pins):    
    super().__init__(led_pins)
    self.led_pins=led_pins

  def on(self,*led_pins):
    leds=led_pins if led_pins else self.led_pins
    for led in leds:
      GPIO.output(led, True)
    
  def off(self,*led_pins):
    leds=led_pins if led_pins else self.led_pins
    for led in leds:
      GPIO.output(led, False)
  
  def alert(self):
    for led in self.led_pins:
      self.on(led)
      time.sleep(0.15)
      self.off(led)
      time.sleep(0.15)

class Buzzer(Alarm_unit):
  def __init__(self, *buzzer_pins):
    super().__init__(buzzer_pins)
    self.buzzer_pins=buzzer_pins
    
  def on(self, *buzzer_pins):
    buzzers=buzzer_pins if buzzer_pins else self.buzzer_pins
    GPIO.output(buzzers, True)

  def off(self, *buzzer_pins):
    buzzers=buzzer_pins if buzzer_pins else self.buzzer_pins
    GPIO.output(buzzers,False)
  
  def alert(self):
    for buzzer in self.buzzer_pins:
      self.on(buzzer)
      time.sleep(0.15)
      self.off(buzzer)
      time.sleep(0.15)
    
def alert_all(*alert_units:Alarm_unit):
  for unit in alert_units:
    unit.alert

def main():
  GPIO.setmode(GPIO.BCM)
  led_pins=14,15
  buzzer_pins=13

  led=LED(*led_pins)
  buzzer=Buzzer(*buzzer_pins)

  alert_all(led, buzzer)

  GPIO.cleanup()

  def __del__():
    GPIO.cleanup()


if __name__=='__main__':
  main()


#   client=bigquery.Client()

#   query=""" 
#     SLECT [num of human]
#     FROM andong-24-team-102.vm_to_bq.[table]

#   """

#   query_job=client.query(query)
#   result=query_job.result()
