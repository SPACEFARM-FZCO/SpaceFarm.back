import imp
from config import server
from config.mongodb import client
from core.winrenboard.main import WinrenBoard
from fastapi import APIRouter,  Request
from models.winrenboard import Delete_zone
router = APIRouter(prefix=server.Server_config.prefix +"/winrenboard",
                   responses=server.Server_config.responses,
                   tags=['winrenboard'])


@router.post("/statistics") 
async def statistics(data:dict,request:Request):    
    return await WinrenBoard.post_statistics(data,request)
 

@router.get("/statistics")
async def statistics(request:Request):    
    return await WinrenBoard.get_statistics(request)


@router.get("/climatezonesettings")
async def statistics(request:Request):    
    return await WinrenBoard.get_climatezonesettings(request)

@router.post("/zones")
async def add_zone(zone:dict,request:Request):
    print(zone)
    return await WinrenBoard.settings_zones(zone,request)

@router.post("/delete_zones")
async def add_zone(zone:Delete_zone,request:Request):
    print(zone)
    return await WinrenBoard.delete_zone(zone,request)


@router.get("/config")
async def add_zone(request:Request):
    return await WinrenBoard.get_config(request)



@router.get("/temperature")
async def get_temperature(number_zone:int,request:Request,filter:str = "week", type:str='day'): 
    return await WinrenBoard.get_graphics(number_zone,filter,type,'air_temperature',request)

@router.get("/c02") 
async def get_c02(number_zone:int,request:Request,filter:str = "week", type:str='day'): 
    return await WinrenBoard.get_graphics(number_zone,filter,type,'c02',request)

@router.get("/humidity") 
async def get_humidity(number_zone:int,request:Request,filter:str = "week", type:str='day'): 
    return await WinrenBoard.get_graphics(number_zone,filter,type,'humidity',request)

@router.get("/VOC") 
async def get_VOC(number_zone:int,request:Request,filter:str = "week", type:str='day'): 
    return await WinrenBoard.get_graphics(number_zone,filter,type,'VOC',request)


from core.rabbitmq.main import Broker
import random
@router.get("/testrmq")
async def testrmq():
    return await Broker.send_config("test",{"value":random.randint(000,999)})
import random
from datetime import datetime,timedelta
import uuid
@router.get("/stst")
async def stat():
    date_start = datetime.fromtimestamp(1656028800)
    for i in range(0,1200):
        hour = i % 24
        date = int(datetime.strptime((date_start+timedelta(hours=i)).strftime("%d/%m/%Y"), "%d/%m/%Y").timestamp())
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
            "light": True if hour>=6 and hour<21 else False,
            "working_floors": 4,
            "c02": random.randint(90,1300),
            "humidity":random.randint(4,90),
            "air_temperature": random.randint(19,24) if hour>=6 and hour<=21 else random.randint(14,18),
            "daylight_schedule": "6:00 - 21:00",
            "VOC":random.randint(0,1000),
            "watering_schedule": "11 times, 7 minutes each"
            },
            {
            "name": "Bazil",
            "number_zone": 2,
            "light": True if hour>=6 and hour<21 else False,
            "working_floors": 6,
            "humidity":random.randint(4,90),
            "c02": random.randint(90,1300),
            "VOC":random.randint(0,1000),
            "air_temperature": random.randint(19,24) if hour>=6 and hour<=21 else random.randint(14,18),
            "daylight_schedule": "6:00 - 21:00",
            "watering_schedule": "11 times, 7 minutes each"
            }
        ],
        }
        data.update({"date":(date_start+timedelta(hours=i)).timestamp()})
        data.update({"datetext":date_start+timedelta(hours=i)})
        
        db_name = "dev"
        if await client[db_name].statistics.find_one({"date":date}):
            await client[db_name].statistics.update_one({"date":date},{"$push":{"statistics":data}})
        else:
            await client[db_name].statistics.insert_one({"_id":str(uuid.uuid4()),"date":date,"statistics":[data]})
