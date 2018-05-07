# -*- coding:utf-8 -*-
import MySQLdb
import pika
import time
import json
import rlp
import sha3
import binascii

# mysql语句 
insert_into_block      = "INSERT INTO ethereum.error_block(block_number) VALUES (%s)"

# 每次汇报的频率
FREQUENCY = 100

RABBIT_INFO = {
    "host": "localhost",
    "port": 5672,
    "credentials": pika.credentials.PlainCredentials(username="guest", password="guest")
}
BLOCK_QUEUE_NAME = "error_block"
connection = pika.BlockingConnection(pika.ConnectionParameters(**RABBIT_INFO))
channel = connection.channel()
channel.queue_declare(queue=BLOCK_QUEUE_NAME, auto_delete=False, durable=True)
# 连接mysql数据库
db = MySQLdb.connect("localhost", "root", "63982677", "ethereum", charset='utf8' )
cursor = db.cursor()
def callback(ch, method, properties,body):
    save_error_block(body)
    print(body)

def save_error_block(block_number):
    try:
        cursor.execute(insert_into_block,[block_number])
    	if(int(block_number) % 100 ==0 ):
        	db.commit()
        	print("Loading tx to DB from (at %s )"% ( time.asctime(time.localtime())  ))
    except Exception as e:
        print("ERROR",str(e),insert_into_block)

#   开始监听
channel.basic_consume(callback , queue=BLOCK_QUEUE_NAME , no_ack=False)
channel.start_consuming()







