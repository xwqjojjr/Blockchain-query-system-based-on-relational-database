# -*- coding:utf-8 -*-
import MySQLdb
import pika
import time
import json
import rlp
import sha3
import binascii
#from util import Helper


RABBIT_INFO = {
    "host": "localhost",
    "port": 5672,
    "credentials": pika.credentials.PlainCredentials(username="guest", password="guest")
}

BLOCK_QUEUE_NAME = "ethblocks"
FREQUENCY = 500
connection = pika.BlockingConnection(pika.ConnectionParameters(**RABBIT_INFO))
channel = connection.channel()
channel.queue_declare(queue=BLOCK_QUEUE_NAME, auto_delete=False, durable=True)

db = MySQLdb.connect("localhost", "root", "63982677", "ethereum", charset='utf8' )
cursor = db.cursor()

append = []

def callback(ch, method, properties,body):
    block = json.loads(body)
#    for dict in block:
#	print dict,block[dict]
#    print()
    args = [block["number"],block["hash"],block["timestamp"],block["parentHash"],block["nonce"],block["miner"],block["difficulty"],block["size"],block["extraData"]]
#    print args
    cursor.execute("INSERT INTO ethereum.Blocks(block_number, block_hash, timestamp, prev_block_hash, nonce, miner_addr, difficulty, size_bytes, extra_data) VALUES (%s,%s,FROM_UNIXTIME(%s),%s,%s,%s,%s,%s,%s)",args);
    if(block["number"] % FREQUENCY == 0):
        try:
                 print block["number"]
        	 n=db.commit()
		 print(n)
	except Exception as e:
	         print("ERROR",str(e),sql_insert_Blocks)

    ch.basic_ack(delivery_tag=method.delivery_tag)
channel.basic_consume(callback , queue=BLOCK_QUEUE_NAME , no_ack=False)

channel.start_consuming()

