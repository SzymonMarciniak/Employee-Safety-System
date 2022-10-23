import time
import requests

class Alarms:
    def __init__(self) -> None:
        self.ip = "192.168.0.9"

    def start_buzzer(self):
        try:
            requests.get(f"http://{self.ip}/BuzzerOn")
        except: pass 
    
    def stop_buzzer(self):
        try:
            requests.get(f"http://{self.ip}/BuzzerOff")
        except: pass 

    def flash_alarm_on(self, id=1):
        try:
            if id==1:
                nr = ""
            elif id == 2:
                nr = "2"

            requests.get(f"http://{self.ip}/FlashOn{nr}")
        except: pass 

    def flash_alarm_off(self, id=1):
        try:
            if id==1:
                nr = ""
            elif id == 2:
                nr = "2"

            requests.get(f"http://{self.ip}/FlashOff{nr}")
        except: pass 

if __name__ == "__main__":
    alert = Alarms()
    time.sleep(6)
    alert.flash_alarm_on(1)
    time.sleep(9)
    
    alert.flash_alarm_on(2)
    
    
    
   
    
