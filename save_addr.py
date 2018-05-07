# -*- coding:utf-8 -*-
import MySQLdb
import pika
import time
import json
import rlp
import sha3
import binascii

# mysql语句 

insert_into_block      = "INSERT INTO ethereum.Addresses(addr,addr_type) VALUES (%s,%s)"
'''
create table Addresses(
addr varchar(100),
addr_type int,
eth bigint
);
'''

# 每次汇报的频率
FREQUENCY = 100
# 表明交易的状态 0:contract Address  1:Person Address
# RABBITMQ信息,创建connection和channel
RABBIT_INFO = {
    "host": "localhost",
    "port": 5672,
    "credentials": pika.credentials.PlainCredentials(username="guest", password="guest")
}
BLOCK_QUEUE_NAME = "Address"
connection = pika.BlockingConnection(pika.ConnectionParameters(**RABBIT_INFO))
channel = connection.channel()
channel.queue_declare(queue=BLOCK_QUEUE_NAME, auto_delete=False, durable=True)
db = MySQLdb.connect("localhost", "root", "63982677", "ethereum", charset='utf8' )
cursor = db.cursor()
addr = ''
address_type = -1
count = 0
def callback(ch,method,properties,body):
        global addr 
	global address_type 
        global count
        print(len(body))
	if(len(body)>2):
		addr = body
	else:
		address_type = body
	save_address(addr,address_type)
        count  = count +1

def save_address(addr,address_type):
    insert_into_args 	= [addr,address_type ]
    print(insert_into_args)
    try:
        cursor.execute(insert_into_block,insert_into_args)
        if(count % 500 ==0):
        	db.commit()
        	print("Loading tx to DB  (at %s )"% ( time.asctime(time.localtime())  ))
    except Exception as e:
        print("ERROR",str(e),insert_into_block)
#   开始监听
channel.basic_consume(callback , queue=BLOCK_QUEUE_NAME , no_ack=False)
channel.start_consuming()	














