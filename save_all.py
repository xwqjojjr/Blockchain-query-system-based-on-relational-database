# -*- coding:utf-8 -*-
import MySQLdb
import pika
import time
import json
import rlp
import sha3
import binascii
from tool import Helper
helper = Helper()
# mysql语句               
insert_into_block      = "INSERT INTO ethereum.EthTest_blocks(blockNumber,blockHash,timeStamp,prevBlockHash,minerAddr,txCount,gasUsed) VALUES (%s,%s,FROM_UNIXTIME(%s),%s,%s,%s,%s)"
insert_into_Transactions      = "INSERT INTO EthTest_transactions(blockNumber,blockHash,txHash,txFrom,txTo,txIndex,txInput,txValue,txType) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
insert_into_AddressHistory    = "INSERT INTO EthTest_addresshistory(blockNumber,txHash,addrHash,balance,txGas,fromORto) VALUES (%s,%s,%s,%s,%s,%s)" 
insert_into_addr 			  = "INSERT INTO EthTest_address(addrHash,addrType) VALUES(%s,%s)"

# 每次汇报的频率
FREQUENCY = 100

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

def is_known_contract(contract_address):
        cursor.execute("""SELECT addrType FROM EthTest_address  WHERE addrHash  = %s""", (contract_address,))
        address = cursor.fetchone()
        if address:
            return  1
        else:
            return False

#   在数据库中保存区块
def save_block_to_db(block):
    count = 0
    for tx in block["transactions"]:
	count = count +1
	tx_type = -1
	gas =  int(tx["gas"])*int(tx["gasPrice"])
	try:
		if not tx["to"]:
            		tx_type = 2 
            		contractAddr =str( helper.calculate_contract_address(tx))
	    	
			print "contractAddr=",contractAddr
			print type(contractAddr) 
			#print json.loads(block)
           		insert_into_addr_args = [contractAddr,1]
            		cursor.execute(insert_into_addr , insert_into_addr_args);
	   		insert_into_addr_args = [tx["from"],0]
                        cursor.execute(insert_into_addr , insert_into_addr_args);
 
	   		insert_into_tx_args   = [ tx["blockNumber"],tx["blockHash"],tx["hash"],tx["from"],contractAddr,tx["transactionIndex"],tx["input"],tx["value"],tx_type ]
            		cursor.execute(insert_into_Transactions,insert_into_tx_args)

            		insert_into_addr_from  = [tx["blockNumber"],tx["hash"],tx["from"],tx["value"],gas,0]
            		cursor.execute(insert_into_AddressHistory,insert_into_addr_from)

	                insert_into_addr_to    = [tx["blockNumber"],tx["hash"],contractAddr,tx["value"],gas,1]
           		cursor.execute(insert_into_AddressHistory,insert_into_addr_to)


       		else:
            	# Should check what the 'to' field is here (contract/person)
            		tx_type = 0
            		if is_known_contract(tx["to"]):
            			tx_type = 1
            			insert_into_addr_args = [tx["to"],1]
            			cursor.execute(insert_into_addr , insert_into_addr_args)
            		insert_into_addr_args = [tx["to"],0]
            		cursor.execute(insert_into_addr , insert_into_addr_args)
	    		insert_into_addr_args = [tx["from"],0]
            		cursor.execute(insert_into_addr , insert_into_addr_args)
            		insert_into_tx_args   = [ tx["blockNumber"],tx["blockHash"],tx["hash"],tx["from"],tx["to"],tx["transactionIndex"],tx["input"],tx["value"],tx_type ]
            		cursor.execute(insert_into_Transactions,insert_into_tx_args)
            		insert_into_addr_from  = [tx["blockNumber"],tx["hash"],tx["from"],tx["value"],gas,0]
       	    		cursor.execute(insert_into_AddressHistory,insert_into_addr_from)
	    		insert_into_addr_to    = [tx["blockNumber"],tx["hash"],tx["to"],tx["value"],gas,1]
            		cursor.execute(insert_into_AddressHistory,insert_into_addr_to)
        except Exception as e:
	    print("ERROR",str(e),tx)
#	print tx
    insert_into_block_args = [block["number"],block["hash"],block["timestamp"],block["parentHash"],block["miner"],count,block["gasUsed"]]
    cursor.execute(insert_into_block , insert_into_block_args);
    if(block["number"] % FREQUENCY == 0):
    	try:
            n=db.commit()
            print("Loading %d blocks to DB from #%s (at %s )"% (FREQUENCY,block["number"], time.asctime(time.localtime())  ))
    	except Exception as e:
      	    print("ERROR",str(e))
#   把区块、交易和账户等信息保存到数据库中
def save_to_db(block):
    save_block_to_db(block);

#   开始监听
channel.basic_consume(callback , queue=BLOCK_QUEUE_NAME , no_ack=False)
channel.start_consuming()
