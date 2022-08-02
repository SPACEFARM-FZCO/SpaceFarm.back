import pika

KEY ="4TVvFuubrExcYwxASDLpRaCGgKgmk3ac"
credentials = pika.PlainCredentials('spacefarmrmq', 'TGbS4E382KhwKQk')
parameters = pika.ConnectionParameters('rabbitmq',
                                   5672,
                                   '/',
                                   credentials)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()