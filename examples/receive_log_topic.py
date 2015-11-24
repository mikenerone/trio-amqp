#!/usr/bin/env python
"""
    Rabbitmq.com pub/sub example

    https://www.rabbitmq.com/tutorials/tutorial-five-python.html

"""

import asyncio
import aioamqp

import random
import sys


@asyncio.coroutine
def callback(body, envelope, properties):
    print("consumer {} recved {} ({})".format(envelope.consumer_tag, body, envelope.delivery_tag))


@asyncio.coroutine
def receive_log():
    try:
        transport, protocol = yield from aioamqp.connect('localhost', 5672)
    except aioamqp.AmqpClosedConnection:
        print("closed connections")
        return

    channel = yield from protocol.channel()
    exchange_name = 'topic_logs'
    # TODO let rabbitmq choose the queue name
    queue_name = 'queue-%s' % random.randint(0, 10000)

    yield from channel.exchange(exchange_name, 'topic')

    yield from asyncio.wait_for(channel.queue(queue_name, durable=False, auto_delete=True), timeout=10)

    binding_keys = sys.argv[1:]
    if not binding_keys:
        print("Usage: %s [binding_key]..." % (sys.argv[0],))
        sys.exit(1)

    for binding_key in binding_keys:
        yield from asyncio.wait_for(channel.queue_bind(exchange_name='topic_logs',
                                                       queue_name=queue_name,
                                                       routing_key=binding_key), timeout=10)

    print(' [*] Waiting for logs. To exit press CTRL+C')

    yield from asyncio.wait_for(channel.basic_consume(callback,
        queue_name=queue_name), timeout=10)


asyncio.get_event_loop().run_until_complete(receive_log())
