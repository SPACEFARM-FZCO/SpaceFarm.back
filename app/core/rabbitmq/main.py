from distutils.command.config import config


from config.rabbitmq import channel,KEY
import json
class Broker:
    async def send_config(exchange_farm,body_value):
        channel.queue_declare(queue=exchange_farm)
        channel.basic_publish(exchange='',
                      routing_key=exchange_farm,
                      body=json.dumps(body_value))
        return
  