    
from config.rabbitmq import channel,KEY
import json
def main():

    queue_farm = 'test'
    channel.queue_declare(queue=queue_farm)

    def callback(ch, method, properties, body):
        config = json.loads(body.decode('utf-8'))        
        print('body',config)
        
    channel.basic_consume(queue=queue_farm, on_message_callback=callback, auto_ack=False)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Error connection')
        