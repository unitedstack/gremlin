#!/usr/bin/env python
import argparse
import pika
import threading

parser = argparse.ArgumentParser("./stress_mq.py",
                                 description='Publish messages to RabbitMQ')
parser.add_argument('-H', '--rabbit-host', default='localhost',
                    help="RabbitMQ Host Address")
parser.add_argument('-u', '--rabbit-username', default='guest',
                    help="RabbitMQ username")
parser.add_argument('-p', '--rabbit-password', default='guest',
                    help="RabbitMQ password")
parser.add_argument('--rabbit-exchange', default='gremlin',
                    help="The exchange to stress in RabbitMQ")
parser.add_argument('--exchange-durable', default='False',
                    help="Set exchange to durable or not")
parser.add_argument('--exchange-auto-delete', default='False',
                    help="Set exchange to auto_delete or not")
parser.add_argument('--rabbit-queue', default='notifications.info',
                    help="The queue to stress in RabbitMQ")
parser.add_argument('--queue-durable', default='False',
                    help="Set queue to durable or not")
parser.add_argument('--queue-auto-delete', default='False',
                    help="Set queue to auto_delete or not")
parser.add_argument('--routing-key', default='notifications.info',
                    help="The routing_key the queue will bind with")
parser.add_argument('-t', '--threads', type=int, default=100,
                    help="The threading number will spawned to do publish messages")
parser.add_argument('-n', '--msg-per-thread', type=int, default=10000,
                    help="Message number every thread will publish")
args = parser.parse_args()

credentials = pika.PlainCredentials(args.rabbit_username, args.rabbit_password)
parameters = pika.ConnectionParameters(host=args.rabbit_host,
                                       credentials=credentials)

def str2bool(v):
    return v.lower() in ('true', 'yes', '1')

def publish():
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()  

    channel.exchange_declare(exchange=args.rabbit_exchange,
                             durable=str2bool(args.exchange_durable),
                             auto_delete=str2bool(args.exchange_auto_delete),
                             type="topic")
    channel.queue_declare(queue=args.rabbit_queue,
                          durable=str2bool(args.queue_durable),
                          auto_delete=str2bool(args.queue_auto_delete))
    channel.queue_bind(args.rabbit_queue, args.rabbit_exchange,
                       args.routing_key)

    message = 'Gremlin Coming!'
    count = 0
    while count < args.msg_per_thread:
        channel.basic_publish(exchange=args.rabbit_exchange,
                              routing_key=args.routing_key,
                              body=message)
        count = count + 1
    connection.close()

threads = [threading.Thread(target=publish) for i in range(args.threads)]

for t in threads:
    t.start()

for t in threads:
    t.join()
