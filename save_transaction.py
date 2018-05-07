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
insert_into_Transactions      = "INSERT INTO ethereum.Transactions(block_number,block_hash,tx_from,tx_to,tx_hash,tx_index,tx_input,tx_value,tx_type,nonce) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
insert_into_Tx_To = "INSERT INTO ethereum.Tx_To(addr,tx_hash) VALUES (%s,%s)"
insert_into_Tx_From =  "INSERT INTO ethereum.Tx_From(addr,tx_hash) VALUES (%s,%s)"

'''
CREATE TABLE `Transactions` (
  `block_number` int(11) DEFAULT NULL,
  `block_hash` varchar(100) DEFAULT NULL,
  `tx_from` varchar(100) DEFAULT NULL,
  `tx_hash` varchar(100) DEFAULT NULL,
  `tx_index` int(11) DEFAULT NULL,
  `tx_input` varchar(10000) DEFAULT NULL,
  `tx_value` varchar(100) DEFAULT NULL,
  `tx_type` int(11) DEFAULT NULL,
  `nonce` int(11) DEFAULT NULL,
  `tx_to` varchar(100) DEFAULT NULL
);

drop table Tx_From;
create table Tx_From(
addr varchar(70),
tx_hash varchar(70)
);
drop table Tx_To;
create table Tx_To(
addr varchar(70),
tx_hash varchar(70)
);
'''

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
#	print(tx)
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
    insert_into_tx_args    = [ tx["blockNumber"],tx["blockHash"],tx["from"],tx["to"],tx["hash"],tx["transactionIndex"],tx["input"],tx["value"],tx_type,tx["nonce"] ]
    try:
        cursor.execute(insert_into_Transactions,insert_into_tx_args)
#        db.commit()
	cursor.execute(insert_into_Tx_From,[tx["from"],tx["hash"]])
#	db.commit()
	cursor.execute(insert_into_Tx_To,[tx["to"],tx["hash"]])
#        print( db.commit())
	if(tx["blockNumber"] % FREQUENCY == 0):
            db.commit()
            print("Loading tx to DB from #%s (at %s )"% (tx["blockNumber"], time.asctime(time.localtime())  ))
    except Exception as e:
        print("ERROR",str(e))
#   开始监听
channel.basic_consume(callback , queue=BLOCK_QUEUE_NAME , no_ack=False)
channel.start_consuming()
