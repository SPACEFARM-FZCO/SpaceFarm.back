from distutils.command.config import config
from fastapi import  Request,HTTPException
from config.mongodb import client
from datetime import datetime,timedelta
from core.winrenboard.utils import validation,get_timetable_list,get_graphics_statistics
from core.rabbitmq.main import Broker
from models.winrenboard import Delete_zone

import uuid
class WinrenBoard:

    async def post_statistics(data:dict,request:Request):
        db_name = await WinrenBoard.select_db(request)
        data['date'] = int(datetime.now().timestamp())
        date = datetime.strptime(datetime.now().strftime("%d/%m/%Y"), "%d/%m/%Y").timestamp()
        if await client[db_name].statistics.find_one({"date":date}):
            client[db_name].statistics.update_one({"date":date},{"$push":{"statistics":data}})
        else:
            client[db_name].statistics.insert_one({"_id":str(uuid.uuid4()),"date":date,"statistics":[data]})
        return {"result":"ok"}

    async def get_statistics(request:Request):
        db_name = await WinrenBoard.select_db(request)
        statistics = client[db_name].statistics.find({}).sort("date", -1).limit(1)
        config = await client.spacefarm.configs.find_one({"account":db_name})
        if not config:
            raise HTTPException(status_code=404)
        async for doc in statistics:
            return await validation(doc['statistics'][-1],config)
        return []

    
    async def get_config(request:Request):
        db_name = await WinrenBoard.select_db(request)
        config = await client.spacefarm.configs.find_one({"account":db_name},{"_id":0,"account":0})    
        await Broker.send_config("test",config)
        return config

    async def get_climatezonesettings(request:Request):
        db_name = await WinrenBoard.select_db(request)
        config = await client.spacefarm.configs.find_one({"account":db_name})
        settings = {"day_temp":config['climate']['day_temp'],
                    "night_temp":config['climate']['night_temp'],
                    "co2_range":f"{config['climate']['co2_bottom']}-{config['climate']['co2_top']}",
                    "humidity_range":f"{config['climate']['humidity_bottom']}-{config['climate']['humidity_top']}",
                    "ph_range":f"{config['solution']['ph_bottom']}-{config['solution']['ph_top']}",
                    "ec_range":f"{config['solution']['ph_bottom']}-{config['solution']['ph_top']}",
                    "nutrient_range":"18-18",
                    "volume_tank":f"{config['solution']['volume_tank']}L",
                    "speedpomp":f"{config['solution']['SpeedPomp']}L/Мin",
                    "zones":[]
                    }
        for zone in config['growing_zones']:
            if zone['watering_period']['use_timetable']:
            
                watering_schedule_count_data = None
                watering_schedule_one_time = True
                watering_schedule_list = []
                for time in zone['watering_period']['timetable']:
                    watering_schedule_data = datetime.strptime(time['end_watering'],"%Y-%m-%dT%H:%M:%S")-datetime.strptime(time['start_watering'],"%Y-%m-%dT%H:%M:%S")
                    watering_schedule_list.append(f"{time['start_watering'].split('T')[1][:5]}-{time['end_watering'].split('T')[1][:5]}")
                    watering_schedule_data = int(watering_schedule_data.total_seconds() / 60.0)
                    if watering_schedule_count_data and watering_schedule_data != watering_schedule_count_data or not watering_schedule_one_time:
                        watering_schedule_one_time = False
                    else:
                        watering_schedule_count_data = watering_schedule_data
                if watering_schedule_one_time:
                    watering_schedule_value = f"{len(zone['watering_period']['timetable'])} times, {watering_schedule_count_data} minutes each"
                else:
                    watering_schedule_value = ','.join(watering_schedule_list)

            else:
                watering_schedule_value = f"{zone['watering_period']['cyclicality']['period']} period, {zone['watering_period']['cyclicality']['duration']} duration"
            daylight_schedule_start_day = datetime.strptime(zone['day_light']['start_day'],"%Y-%m-%dT%H:%M:%S")
            daylight_schedule_start_day_minute = f"0{daylight_schedule_start_day.minute}" if daylight_schedule_start_day.minute < 10 else daylight_schedule_start_day.minute
            daylight_schedule_end_day = datetime.strptime(zone['day_light']['end_day'],"%Y-%m-%dT%H:%M:%S")
            daylight_schedule_end_day_minute = f"0{daylight_schedule_end_day.minute}" if daylight_schedule_end_day.minute < 10 else daylight_schedule_end_day.minute
            
            settings['zones'].append({"name":zone['name'],
                                      "number_zone":zone['number_zone'],
                                      "modbus_id":zone['modbus_id'],
                                      "daylight_schedule":f"{daylight_schedule_start_day.hour}:{daylight_schedule_start_day_minute} - {daylight_schedule_end_day.hour}:{daylight_schedule_end_day_minute}",
                                      "watering_schedule":watering_schedule_value,
                                      "watering_schedule_type":'Individual'if zone['watering_period']['use_timetable'] else 'Cycle'
                            })
        return settings

    async def delete_zone(zone:Delete_zone,request:Request):
        db_name = await WinrenBoard.select_db(request)
        client.spacefarm.configs.update_one({"account":db_name},{ "$pull": { "growing_zones": { "number_zone": zone.number_zone,
                                                                                            "modbus_id":zone.modbus_id} }},False,True)
        return

    async def settings_zones(zone:dict,request:Request):
        date = datetime.now().strftime("%Y-%m-%dT")
        daylight_schedule = zone['daylight_schedule'].split(' - ')
        db_name = await WinrenBoard.select_db(request)
        config = await client.spacefarm.configs.find_one({"account":db_name})
        for growing_zones in config['growing_zones']:
            if growing_zones['number_zone'] == int(zone['number_zone']):
                update_config = {"growing_zones.$.name":zone['name'],
                                "growing_zones.$.modbus_id":int(zone['modbus_id']),
                                "growing_zones.$.day_light.start_day":f"{date}{daylight_schedule[0]}:00",
                                "growing_zones.$.day_light.end_day":f"{date}{daylight_schedule[1]}:00"}
                if not isinstance(zone['watering_schedule'],str):
                    if isinstance(zone['watering_schedule'],list):
                        timetable_list = await get_timetable_list(zone,date)
                        update_config.update({"growing_zones.$.watering_period.use_timetable":True,
                                            "growing_zones.$.watering_period.use_cyclicality":False,
                                            "growing_zones.$.watering_period.timetable":timetable_list,
                                            "growing_zones.$.watering_period.cyclicality":{},
                                            })
                    else:
                    
                        if int(zone['watering_schedule']['interval']) < int(zone['watering_schedule']['duration']):
                            raise HTTPException(status_code=409,detail="The duration of watering should always be less than the period.")
                        update_config.update({"growing_zones.$.watering_period.use_timetable":False,
                                            "growing_zones.$.watering_period.use_cyclicality":True,
                                            "growing_zones.$.watering_period.timetable":[],
                                            "growing_zones.$.watering_period.cyclicality.period":int(zone['watering_schedule']['interval']),
                                            "growing_zones.$.watering_period.cyclicality.duration":int(zone['watering_schedule']['duration'])})
                client.spacefarm.configs.update_one({"account":db_name,"growing_zones.number_zone":int(zone['number_zone'])},{"$set":update_config})
                return

        new_zone = {
            "name": zone['name'],
            "number_zone": int(zone['number_zone']),
            "modbus_id": int(zone['modbus_id']),
            "day_light": {
                "start_day":f"{date}{daylight_schedule[0]}:00",
                "end_day":f"{date}{daylight_schedule[1]}:00",
                "personal_floors_control":False,
                "forced_on":False,
                "forced_off":False,
                "floors":[]
            },
            "manual_watering":False,
            "watering_period":{"watering_only_light_day":False}
        }
        if isinstance(zone['watering_schedule'],list):
            timetable_list = await get_timetable_list(zone,date)
            new_zone['watering_period'].update({"use_timetable":True,
                                                "use_cyclicality":False,
                                                "timetable":timetable_list,
                                                "cyclicality":{}})
        else:
            if isinstance(zone['watering_schedule'],str):
                raise HTTPException(status_code=409,detail="You cannot change this data")
            if int(zone['watering_schedule']['interval']) < int(zone['watering_schedule']['duration']):
                raise HTTPException(status_code=409,detail="The duration of watering should always be less than the period.")
            new_zone['watering_period'].update({"use_timetable":False,
                                                "use_cyclicality":True,
                                                "timetable":[],
                                                "cyclicality":{"period":int(zone['watering_schedule']['interval']),
                                                                "duration":int(zone['watering_schedule']['duration'])}})
        client.spacefarm.configs.update_one({"account":db_name},{"$push":{"growing_zones":new_zone}})
        return

    
    
    async def get_graphics(number_zone:int,filter:str,type:str,parameter:str,request:Request):
        
        day = True if type == 'day' else False
        db_name = await WinrenBoard.select_db(request)
        date = int(datetime.strptime(datetime.now().strftime("%d/%m/%Y"), "%d/%m/%Y").timestamp())
        validation_data = await WinrenBoard.get_statistics(request)
        if not validation_data:
            return {}
        data = {
            "chart":{"data":[],"categories":[]},
            "temp_solution":validation_data['temp_solution'],
            'c02':validation_data['co2'],
            "ppm":validation_data['ppm'],
            "ec":validation_data['ec'],
            "ph":validation_data['ph'],
            "working_zones":len(validation_data['zones'])
        }  
        for zone in validation_data['zones']:
            if zone['number_zone'] == number_zone:
                data.update({'name':zone['name'],'VOC':zone['VOC'],'humidity':{"value":zone['humidity']}})
    
        if filter == "day":
            zone_db = await client[db_name].statistics.find_one({"date":date,
                                                            "statistics":{"$elemMatch":{"zones":{"$elemMatch":{"number_zone":number_zone}}}}},{"statistics":1})
            if not zone_db:
                return data
            chart_data,chart_categories = await get_graphics_statistics(zone_db,number_zone,day,parameter)
            if len(chart_data) != 24:
                last = 24 - len(zone_db['statistics'])
                date = int(datetime.strptime((datetime.now()-timedelta(days=1)).strftime("%d/%m/%Y"), "%d/%m/%Y").timestamp())
                zone_db = await client[db_name].statistics.find_one({"date":date,
                                                            "statistics":{"$elemMatch":{"zones":{"$elemMatch":{"number_zone":number_zone}}}}},{"statistics":1})                
                if not zone_db:
                    return data
                chart_data_list = []
                chart_categories_list = []
                for statistics in zone_db['statistics'][len(zone_db['statistics'])-last:]:
                    for zone in statistics['zones']:
                        if zone['number_zone'] == number_zone and zone['light'] == day:
                            chart_data_list.append(zone[parameter])
                            chart_categories_list.append(datetime.fromtimestamp(statistics['date']).strftime("%H"))
                            
                data['chart']['data'] = chart_data_list + chart_data
                data['chart']['categories'] = chart_categories_list + chart_categories
                return data

        if filter == "week" or filter == "month":
            if filter == "week":
                date_week = int(datetime.strptime((datetime.now()-timedelta(days=7)).strftime("%d/%m/%Y"), "%d/%m/%Y").timestamp())
                strftime_data = "%a"
            else:
                date_week = int(datetime.strptime((datetime.now()-timedelta(days=31)).strftime("%d/%m/%Y"), "%d/%m/%Y").timestamp())
                strftime_data = "%d/%m"
            async for doc in client[db_name].statistics.find({"date":{"$gte":date_week,"$lte":date},
                                                            "statistics":{"$elemMatch":{"zones":{"$elemMatch":{"number_zone":number_zone}}}}}).sort("date", 1):
                temperature = 0
                count_temperature = 0
                for statistics in doc['statistics']:
                    for zone in statistics['zones']:
                        if zone['number_zone'] == number_zone and zone['light'] == day:
                                count_temperature += 1
                                temperature += zone[parameter]
                temperature = int(temperature / count_temperature)
                data['chart']['data'].append(temperature)
                data['chart']['categories'].append(datetime.fromtimestamp(doc['date']).strftime(strftime_data))   
        return data
    
    
    async def select_db(request:Request):
        return "dev"
