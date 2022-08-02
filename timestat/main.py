import requests
import random
from timeloop import Timeloop
from datetime import timedelta

tl = Timeloop()

@tl.job(interval=timedelta(minutes=30))
def send_stat():
    hour = random.randint(0,23)
    
    data = {
      "spaceID": 1,
      "ppm": random.randint(580,710) ,
      "ec": random.randint(53,67)/10,
      "ph": random.randint(53,67)/10,
      "temp_solution": 20,
      "consumed_KW": 30,
      "zones": [
        {
          "name": "Microgreen",
          "number_zone": 1,
          "light": True if hour>=6 and hour<=21 else False,
          "working_floors": 4,
          "c02": 450,
          "air_temperature": random.randint(19,24) if hour>=6 and hour<=21 else random.randint(14,18),
          "daylight_schedule": "6:00 - 21:00",
          "watering_schedule": "11 times, 7 minutes each"
        },
        {
          "name": "Bazil",
          "number_zone": 2,
          "light": True if hour>=6 and hour<=21 else False,
          "working_floors": 6,
          "c02": 600,
          "air_temperature": random.randint(19,24) if hour>=6 and hour<=21 else random.randint(14,18),
          "daylight_schedule": "6:00 - 21:00",
          "watering_schedule": "11 times, 7 minutes each"
        }
      ],
    },
    print(data)
    return



send_stat()

#tl.start(block=True)