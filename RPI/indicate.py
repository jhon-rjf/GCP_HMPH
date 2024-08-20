import os
import RPi.GPIO as GPIO
from abc import ABC, abstractmethod
from google.cloud import bigquery
import time
import itertools

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcloud-team-project-credential-key.json'
GPIO.setmode(GPIO.BCM)

class Alarm_unit(ABC):
  def __init__(self, *pins:tuple) -> None:
    self.pins=pins

    for pin in pins:
      GPIO.setup(pin, GPIO.OUT)

  @abstractmethod
  def indicate_safe(self) -> None:
    pass

  @abstractmethod
  def indicate_caution(self) -> None:
    pass

  @abstractmethod
  def indicate_watch(self) -> None:
    pass

  @abstractmethod
  def alert_warining(self) -> None:
    pass

  def __del__(self) -> None:
    for pin in self.pins:
      GPIO.setup(pin, GPIO.IN)

class LED(Alarm_unit):
  def __init__(self, *led_pins:tuple):    
    super().__init__(led_pins)
    self.led_pins=led_pins

  def on(self,*led_pins) -> None:
    leds=led_pins if led_pins else self.led_pins
    for led in leds:
      GPIO.output(led, True)
    
  def off(self,*led_pins) -> None:
    leds=led_pins if led_pins else self.led_pins
    for led in leds:
      GPIO.output(led, False)

  def indicate_safe(self) -> None:
    self.off()
    for led in self.led_pins:
      self.off(led)

  def indicate_caution(self) -> None:
    self.off()
    self.on(self.led_pins[0])
  
  def indicate_watch(self) -> None:
    self.off()
    self.on()
  
  def alert_warining(self) -> None:
    self.off()
    for led in self.led_pins:
      self.on(led)
      time.sleep(0.15)
      self.off(led)
      time.sleep(0.15)

class Buzzer(Alarm_unit):
  def __init__(self, buzzer_pins:int) -> None:
    super().__init__(buzzer_pins)
    self.buzzer_pins=buzzer_pins
    
  def on(self, *buzzer_pins) -> None:
    buzzers=buzzer_pins if buzzer_pins else self.buzzer_pins
    for buzzer in buzzers:
      GPIO.output(buzzer, True)

  def off(self, *buzzer_pins) -> None:
    buzzers=buzzer_pins if buzzer_pins else self.buzzer_pins
    for buzzer in buzzers:
      GPIO.output(buzzer,False)

  def indicate_safe(self) -> None:
    self.off()

  def indicate_caution(self) -> None:
    self.off()
  
  def indicate_watch(self) -> None:
    self.off()
  
  def alert_warining(self) -> None:
    pwm=GPIO.PWM(self.buzzer_pins, 640)
    pwm.start(95)

    for scale in range(700,1500,50):
        pwm.ChangeFrequency(scale)
        time.sleep(0.1)

class Enquirer:
  def __init__(self) -> None:
    self.client=bigquery.Client()
  
  def query(self, query) -> int:
    query_job=self.client.query(query)
    results=query_job.result()
    result=next(results,0)
    return result[0]
  
class Controler:
  def __init__(self,*alert_units:Alarm_unit) -> None:
    self.alert_units=alert_units
    self.units_cycle=itertools.cycle(alert_units)

  def set_safe(self):
    for unit in self.alert_units:
      unit.indicate_safe()

  def set_caution(self):
    for unit in self.alert_units:
      unit.indicate_caution()

  def set_watch(self):
    for unit in self.alert_units:
      unit.indicate_watch()

  def set_warning(self) -> None:
    for unit in self.units_cycle:
      unit.alert_warining()

def main():
  area=int(input('면적을 입력해주세요(단위:m^2): '))

  led_pins=14,15
  buzzer_pins=13  
  table_path='andong-24-team-102.vm_to_bq.fin'
  query=f""" 
    SELECT person_count
    FROM {table_path}
    ORDER BY timestamp DESC
    LIMIT 1
    """
  
  led=LED(*led_pins)
  buzzer=Buzzer(buzzer_pins)
  controler=Controler(led,buzzer)
  enquirer=Enquirer()

  density=None
  safe=density<=3.5
  caution=density<=4
  watch=density<=5
  
  while True:
    human_num=enquirer.query(query)
    density=human_num/area
    # warning=5<=density
    
    if safe:
      controler.set_safe()
    elif caution:
      controler.set_caution()
    elif watch:
      controler.set_watch()
    else:
      controler.set_warning()
    print(human_num)
    time.sleep(1)

if __name__=='__main__':
  main()




#평당  3.5안전 4주의 5위험
