from pydantic import BaseModel
from typing import Optional

class Zone(BaseModel):
    name:str
    number_zone:str
    modbus_id:str
    daylight_schedule:str
    watering_schedule:str


class Delete_zone(BaseModel):
    number_zone:int
    modbus_id:int