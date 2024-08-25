import json
import os
import time
import RPi.GPIO as GPIO
from abc import ABC, abstractmethod
from google.cloud import bigquery

GPIO.setmode(GPIO.BCM)

class Unit_Controller(ABC):
  def __init__(self, *pins:int) -> None:
    self.__pins=pins
  
    for pin in self.__pins:
      GPIO.setup(pin, GPIO.OUT)

  @abstractmethod
  def set_safe(self) -> None:
    pass

  @abstractmethod
  def set_caution(self) -> None:
    pass

  @abstractmethod
  def set_watch(self) -> None:
    pass

  @abstractmethod
  def set_warning(self) -> None:
    pass

  def __del__(self) -> None:
    for pin in self.__pins:
      GPIO.setup(pin, GPIO.IN)

class LED_Controller(Unit_Controller):
  def __init__(self, *led_pins:int) -> None:    
    super().__init__(*led_pins)

  def _on(self,*led_pins) -> None:
    leds=led_pins if led_pins else self.__pins
    for led in leds:
      GPIO.output(led, True)

  def _off(self,*led_pins) -> None:
    leds=led_pins if led_pins else self.__pins
    for led in leds:
      GPIO.output(led, False)

  def set_safe(self) -> None:
    self._off()

  def set_caution(self) -> None:
    self._off()
    self._on(self.__pins[0])

  def set_watch(self) -> None:
    self._on()

  def set_warning(self) -> None:
    self._off()
    for led in self.__pins:
      self._on(led)
      time.sleep(0.15)
      self._off(led)
      time.sleep(0.15)

class Buzzer_Controller(Unit_Controller):
  def __init__(self, *buzzer_pins:int) -> None:
    super().__init__(*buzzer_pins)
    
  def _on(self, *buzzer_pins) -> None:
    buzzers=buzzer_pins if buzzer_pins else self.__pins
    for buzzer in buzzers:
      GPIO.output(buzzer, True)

  def _off(self, *buzzer_pins) -> None:
    buzzers=buzzer_pins if buzzer_pins else self.__pins
    for buzzer in buzzers:
      GPIO.output(buzzer,False)

  def set_safe(self) -> None:
    self._off()

  def set_caution(self) -> None:
    self._off()
  
  def set_watch(self) -> None:
    self._off()
  
  def set_warning(self) -> None:
    for pin in self.__pins:
      pwm=GPIO.PWM(pin, 640)
      pwm.start(95)
      for scale in range(700,1500,50):
        pwm.ChangeFrequency(scale)
        time.sleep(0.1)

class Integrated_Controller:
  def __init__(self, *alert_units:Unit_Controller) -> None:
    self.alert_units=alert_units

  def set_safe(self) -> None:
    for unit in self.alert_units:
      unit.set_safe()

  def set_caution(self) -> None:
    for unit in self.alert_units:
      unit.set_caution()

  def set_watch(self) -> None:
    for unit in self.alert_units:
      unit.set_watch()

  def set_warning(self) -> None:
    for unit in self.alert_units:
      unit.set_warning()

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
  settings_path=os.path.join('settings','indicate_settings.json')
  try:
    with open(settings_path, 'r', encoding='utf-8') as file:
      setting_file_data=json.load(file)
      led_pins=setting_file_data['led_pins']
      buzzer_pins=setting_file_data['buzzer_pins']
      credential_path=setting_file_data['credential_path']
      query=setting_file_data['query']
  except FileNotFoundError:
    print('File not found')
  except json.JSONDecodeError as e:
    print('Error decoding json')
    print(f'Error message: {e}')
  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

  measured_area=int(input('면적을 입력해주세요(단위:m^2): '))

  led=LED_Controller(*led_pins)
  buzzer=Buzzer_Controller(*buzzer_pins)
  indicater_controler=Integrated_Controller(led,buzzer)
  enquirer=Enquirer()
  
  while True:
    person_count=enquirer.query(query)
    print(person_count)#테스트용
    density_per_sqmeter=person_count/measured_area

    watch=density_per_sqmeter<=5
    caution=density_per_sqmeter<=4
    safe=density_per_sqmeter<=3.5
    
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
  try:
    main()
  finally:
    GPIO.cleanup()



    # warning=5<=density_per_sqmeter

  """   safty_level=safe+caution+watch+warning
    
    match safty_level:
      case 1:
        return indicater_controler.set_warning()
      case 2:
        return indicater_controler.set_watch()
      case 3:
        return indicater_controler.set_caution()
      case 4:
        return indicater_controler.set_safe() """
