# -*- coding:utf-8 -*-
import MySQLdb
import pika
import time
import json
import rlp
import sha3
import binascii
from util import Helper

# mysql语句 
insert_into_block      = "INSERT INTO ethereum.Transactions(block_number,block_hash,tx_from,tx_hash,tx_index,tx_input,tx_value,tx_type,nonce) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
# 每次汇报的频率
FREQUENCY = 100
# 表明交易的状态 0:Person to person 1:Person to Contract 2:Contract Creation
# RABBITMQ信息,创建connection和channel
RABBIT_INFO = {
    "host": "localhost",
    "port": 5672,
    "credentials": pika.credentials.PlainCredentials(username="guest", password="guest")
}
BLOCK_QUEUE_NAME = "ethtx"
connection = pika.BlockingConnection(pika.ConnectionParameters(**RABBIT_INFO))
channel = connection.channel()
channel.queue_declare(queue=BLOCK_QUEUE_NAME, auto_delete=False, durable=True)

# 连接mysql数据库
db = MySQLdb.connect("localhost", "root", "63982677", "ethereum", charset='utf8' )
cursor = db.cursor()

tx_type = -1
tx = []
count = 0
#   回调函数
def callback(ch, method, properties,body):
    global tx_type
    global tx
    global count
#    print len(body)
    if(len(body) > 100):
    	tx = json.loads(body)
        count = count +1
    else: 
        tx_type=body
        count = count +1
    if (count%2 == 0):
#	print (count,tx_type,tx)
        save_tx(tx,tx_type)
    ch.basic_ack(delivery_tag=method.delivery_tag)

#   在数据库中保存交易

def save_tx(tx,tx_type):
    insert_into_tx_args    = [ tx["blockNumber"],tx["blockHash"],tx["from"],tx["hash"],tx["transactionIndex"],tx["input"],tx["value"],tx_type,tx["nonce"] ]
    try:
        cursor.execute(insert_into_block,insert_into_tx_args)
        if(tx["blockNumber"] % FREQUENCY == 0):
            db.commit()
            print("Loading tx to DB from #%s (at %s )"% (block["number"], time.asctime(time.localtime())  ))
    except Exception as e:
        print("ERROR",str(e),insert_into_block)
#   开始监听
channel.basic_consume(callback , queue=BLOCK_QUEUE_NAME , no_ack=False)
channel.start_consuming()
