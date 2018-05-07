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
insert_into_block      = "INSERT INTO ethereum.Blocks(block_number, block_hash, timestamp, prev_block_hash, nonce, miner_addr, difficulty, size_bytes, extra_data) VALUES (%s,%s,FROM_UNIXTIME(%s),%s,%s,%s,%s,%s,%s)"
insert_into_Tx_Block  =  "INSERT INTO ethereum.Tx_Block(tx_hash,block_number,block_hash) VALUES (%s,%s,%s)"
'''
drop table Blocks;
create table Blocks(
block_number int,
block_hash varchar(100),
timestamp varchar(100),
prev_block_hash varchar(100),
nonce varchar(100),
miner_addr varchar(100),
difficulty bigint,
size_bytes int,
extra_data varchar(2000)
);

create table Tx_Block(
tx_hash varchar(70),
block_number int,
block_hash varchar(70)
);
'''

# 每次汇报的频率
FREQUENCY = 500

# RABBITMQ信息,创建connection和channel
RABBIT_INFO = {
    "host": "localhost",
    "port": 5672,
    "credentials": pika.credentials.PlainCredentials(username="guest", password="guest")
}
BLOCK_QUEUE_NAME = "ethblocks"
connection = pika.BlockingConnection(pika.ConnectionParameters(**RABBIT_INFO))
channel = connection.channel()
channel.queue_declare(queue=BLOCK_QUEUE_NAME, auto_delete=False, durable=True)

# 连接mysql数据库
db = MySQLdb.connect("localhost", "root", "63982677", "ethereum", charset='utf8' )
cursor = db.cursor()
# 定义一个队列存储地址、块hash和地址类型(账户 or 合约)
pending_addresses = []

#   回调函数
def callback(ch, method, properties,body):
    save_to_db(json.loads(body))
    ch.basic_ack(delivery_tag=method.delivery_tag)

#   把地址\块hash\地址类型存到队列pending_addresses中
def queue_address_for_insertion(address, block_hash, address_type=0):
    pending_addresses.append((address, block_hash, address_type))

#   在数据库中保存区块
def save_block_to_db(block):
    insert_into_block_args = [block["number"],block["hash"],block["timestamp"],block["parentHash"],block["nonce"],block["miner"],block["difficulty"],block["size"],block["extraData"]]
    cursor.execute(insert_into_block , insert_into_block_args);
    for tx in block["transactions"]:
#	print tx["hash"]
        insert_into_Tx_Block_args = [tx["hash"],block["number"],block["hash"]]
#        print(insert_into_Tx_Block_args)
   	cursor.execute(insert_into_Tx_Block , insert_into_Tx_Block_args)
    if(block["number"] % FREQUENCY == 0):
        try:
                 n=db.commit()
                 print("Loading %d blocks to DB from #%s (at %s )"% (FREQUENCY,block["number"], time.asctime(time.localtime())  ))
        except Exception as e:
                 print("ERROR",str(e),sql_insert_Blocks)
#   把区块、交易和账户等信息保存到数据库中
def save_to_db(block):
    save_block_to_db(block);

#   开始监听
channel.basic_consume(callback , queue=BLOCK_QUEUE_NAME , no_ack=False)
channel.start_consuming()
