import os
import RPi.GPIO as GPIO
from abc import ABC, abstractmethod
from google.cloud import bigquery
import time
import itertools

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcloud-team-project-credential-key.json'
GPIO.setmode(GPIO.BCM)

class Indicater(ABC):
  def __init__(self, pins:tuple) -> None:
    self.pins=pins
  
    for pin in self.pins:
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

class LED(Indicater):
  def __init__(self, *led_pins) -> None:    
    super().__init__(led_pins)

  def on(self,*led_pins) -> None:
    leds=led_pins if led_pins else self.pins
    for led in leds:
      GPIO.output(led, True)

  def off(self,*led_pins) -> None:
    leds=led_pins if led_pins else self.pins
    for led in leds:
      GPIO.output(led, False)

  def indicate_safe(self) -> None:
    self.off()

  def indicate_caution(self) -> None:
    self.off()
    self.on(self.pins[0])

  def indicate_watch(self) -> None:
    self.on()

  def alert_warining(self) -> None:
    self.off()
    for led in self.pins:
      self.on(led)
      time.sleep(0.15)
      self.off(led)
      time.sleep(0.15)

class Buzzer(Indicater):
  def __init__(self, *buzzer_pins:tuple) -> None:
    super().__init__(buzzer_pins)
    
  def on(self, *buzzer_pins) -> None:
    buzzers=buzzer_pins if buzzer_pins else self.pins
    for buzzer in buzzers:
      GPIO.output(buzzer, True)

  def off(self, *buzzer_pins) -> None:
    buzzers=buzzer_pins if buzzer_pins else self.pins
    for buzzer in buzzers:
      GPIO.output(buzzer,False)

  def indicate_safe(self) -> None:
    self.off()

  def indicate_caution(self) -> None:
    self.off()
  
  def indicate_watch(self) -> None:
    self.off()
  
  def alert_warining(self) -> None:
    for pin in self.pins:
      pwm=GPIO.PWM(pin, 640)
      pwm.start(95)
      for scale in range(700,1500,50):
        pwm.ChangeFrequency(scale)
        time.sleep(0.1)

class Indicater_Controler:
  def __init__(self, *alert_units:Indicater) -> None:
    self.alert_units=alert_units
    self.units_cycle=itertools.cycle(alert_units)

  def set_safe(self) -> None:
    for unit in self.alert_units:
      unit.indicate_safe()

  def set_caution(self) -> None:
    for unit in self.alert_units:
      unit.indicate_caution()

  def set_watch(self) -> None:
    for unit in self.alert_units:
      unit.indicate_watch()

  def set_warning(self) -> None:
    for unit in self.units_cycle:
      unit.alert_warining()

class Enquirer:
  def __init__(self) -> None:
    self.client=bigquery.Client()
  
  def query(self, query) -> int:
    query_job=self.client.query(query)
    result=query_job.result()

    for count in result:  
      person_count=count['person_count']
    return person_count

def main() -> None:
  measured_area=int(input('면적을 입력해주세요(단위:m^2): '))
  led_pins=14,15
  buzzer_pins=13,
  table_path='andong-24-team-102.vm_to_bq.test0807'
  query=f""" 
    SELECT person_count
    FROM {table_path}
    ORDER BY timestamp DESC
    LIMIT 1
    """

  led=LED(*led_pins)
  buzzer=Buzzer(*buzzer_pins)
  indicater_controler=Indicater_Controler(led,buzzer)
  enquirer=Enquirer()
  
  while True:
    person_count=enquirer.query(query)
    density_per_sqmeter=person_count/measured_area

    warning=5<=density_per_sqmeter
    watch=density_per_sqmeter<=5
    caution=density_per_sqmeter<=4
    safe=density_per_sqmeter<=3.5

    '''
    hazrd_level=safe+caution+watch+warning
    
    match hazrd_level:
      case 1:
        return indicater_controler.set_warning()
      case 2:
        return indicater_controler.set_watch()
      case 3:
        return indicater_controler.set_caution()
      case 4:
        return indicater_controler.set_safe()
    '''
    if safe:
      indicater_controler.set_safe()
    elif caution:
      indicater_controler.set_caution()
    elif watch:
      indicater_controler.set_watch()
    else:
      indicater_controler.set_warning()
    
    time.sleep(1)

if __name__=='__main__':
  main()


