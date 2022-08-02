async def validation(statistics,config):
    validation_statistics={"temp_solution":{"value":statistics["temp_solution"]},
                           "humidity":{"value":"12","color":"green"},
                           "co2":{"value":"23","color":"green"},
                           "ph":{"value":statistics['ph']},
                           "ppm":{"value":statistics['ppm']},
                           "ec":{"value":statistics['ec']},
                           "consumed_KW":statistics['consumed_KW'],
                           "working_zones":len(statistics['zones']),
                           "zone_air_temperature":0,
                           "zone_humidity":0,
                           "zone_c02":0,
                           "zone_VOC":0
                           }

    if statistics['temp_solution'] >= (config['climate']['night_temp'] - config['climate']['hysteresis_temp']) and statistics['temp_solution'] <= (config['climate']['day_temp']+config['climate']['hysteresis_temp']):
        validation_statistics["temp_solution"]['color'] = "green"
    else:
        validation_statistics["temp_solution"]['color'] = "red"

    #if statistics['humidity'] >= config['climate']['humidity_bottom'] and statistics['humidity'] <= config['climate']['humidity_top']:
    #     validation_statistics["humidity"]['color']="green"
    # else:
    #     validation_statistics["humidity"]['color']="red"

    #if statistics['co2'] >= config['climate']['co2_bottom'] and statistics['co2'] <= config['climate']['co2_top']:
    #     validation_statistics["co2"]['color'] ="green"
    #else:
    #     validation_statistics["co2"]['color'] ="red"
        
    if statistics['ph'] >= config['solution']['ph_bottom'] and statistics['ph'] <= config['solution']['ph_top']:
        validation_statistics["ph"]['color'] = "red"
    else:
        validation_statistics["ph"]['color'] = "red" 

    if statistics['ppm'] >= config ['solution']['ppm_bottom'] and statistics['ppm'] <= config ['solution']['ppm_top']:
        validation_statistics["ppm"]['color'] = validation_statistics["ec"]['color'] = "red" 
    else:
        validation_statistics["ppm"]['color'] = validation_statistics["ec"]['color'] = "red"
    validation_statistics['zones'] = statistics['zones']

    for zone in statistics['zones']:
        validation_statistics['zone_air_temperature'] += zone['air_temperature']
        validation_statistics['zone_humidity'] += zone['humidity']
        validation_statistics['zone_c02'] += zone['c02']
        validation_statistics['zone_VOC'] += zone['VOC']
    validation_statistics['zone_air_temperature'] = int(validation_statistics['zone_air_temperature'] / len(statistics['zones']))
    validation_statistics['zone_humidity'] = int(validation_statistics['zone_humidity'] / len(statistics['zones']))
    validation_statistics['zone_c02'] = int(validation_statistics['zone_c02'] / len(statistics['zones']))
    validation_statistics['zone_VOC'] = int(validation_statistics['zone_VOC'] / len(statistics['zones']))
    return validation_statistics



async def get_timetable_list(zone,date):
    timetable_list = []
    for timetable in zone['watering_schedule']:
        timetable_list.append({"number_watering":zone['watering_schedule'].index(timetable) + 1,
                                "start_watering":f"{date}{timetable['start']}:00",
                                "end_watering":f"{date}{timetable['end']}:00"})
    return timetable_list



async def get_graphics_statistics(zone_db,number_zone,day,parameter):
    if not zone_db:
        return [],[]
    chart_data = []
    chart_categories = []
    for stat in zone_db['statistics']:
            for zone in stat['zones']:
                if zone['number_zone'] == number_zone and zone['light'] == day:
                    chart_data.append(zone[parameter])
                    chart_categories.append(stat['datetext'].strftime("%H"))
    return chart_data,chart_categories