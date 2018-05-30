var amqp = require('amqp');
var Web3 = require("web3");
//var BigNumber = require("bignumber.js");
var winston = require("winston");


var RPC_SERVER = "http://localhost:8545";

var web3 = new Web3(new Web3.providers.HttpProvider(RPC_SERVER));

var BLOCK_REWARD = 5,
	FIRST_BLOCK = 0,
	MAXIMUM_BLOCK = web3.eth.blockNumber,
	BLOCKS_AT_A_TIME = 1800,
	BLOCK_QUEUE_TIMEOUT = 1000;


if(!web3.isConnected()){
	winston.log("error", "web3 is not connected to the RPC");
	process.exit(1);
}


var connection = amqp.createConnection({ 'host': 'localhost' });


var queue_block = function (block_number){
	web3.eth.getBlock(block_number, true, function(error, result) {
		if(error) {
			console.log("error", "Error getting block number: " + block_number + ". '" + error + "'");
			connection.publish("error_block",block_number)
		} else {
			if(result){
				//保存交易
				var cur_tx,cur_tx_type;
				for(var i=0 ; i<result.transactions.length;i++){
					cur_tx = result.transactions[i];
					 if(cur_tx.to == null){
                                                cur_tx_type = 2; // Contract Creation
                                        } else {
                                                if(web3.eth.getCode(cur_tx.to) == "0x"){
                                                        cur_tx_type = 0; // Person to Person
                                                        connection.publish("Address",cur_tx.from)
                                                        connection.publish("Address","1")
                                                        connection.publish("Address",cur_tx.to)
                                                        connection.publish("Address","1")
                                                } else {
                                                        cur_tx_type = 1; // Person to Contract
                                                        connection.publish("Address",cur_tx.from)
                                                        connection.publish("Address","1")
                                                        connection.publish("Address",cur_tx.to)
                                                        connection.publish("Address","0")
                                                }
                                        }
                                        //console.log(cur_tx,cur_tx_type)
					connection.publish("ethtx",cur_tx)
					connection.publish("ethtx",cur_tx_type)
 				}
					console.log("info", "Queueing Block #" + block_number + " (with " + result.transactions.length + " transactions).");
				connection.publish("ethblocks", result);
			} else {
				console.log("warn", "No block seen for #" + block_number);
			}
		}
		if(block_number < MAXIMUM_BLOCK){
			queue_block(block_number + 1)
		}
	});
	},
	queue_n_blocks = function(starting_block, n) {
		winston.log("info", "Queueing " + n + " blocks, from " + starting_block);
		for(var i = starting_block; i < (starting_block + n); i++){
			if(i <= MAXIMUM_BLOCK){
				queue_block(i);
			} else {
				winston.log("info", "skipped #" + i);
			}
		}
	};



connection.on('ready', function () {
	winston.log("info", "Rabbit Connection ready, starting queueing in " + BLOCK_QUEUE_TIMEOUT/1000 + "s");
	var repeat_queue_blocks = function(current_block) {
		if(current_block <= MAXIMUM_BLOCK){
			queue_n_blocks(current_block, BLOCKS_AT_A_TIME);
			setTimeout(repeat_queue_blocks.bind(this, (current_block+BLOCKS_AT_A_TIME+1)), BLOCK_QUEUE_TIMEOUT)
		}
	};
	setTimeout(repeat_queue_blocks.bind(this, FIRST_BLOCK), BLOCK_QUEUE_TIMEOUT);
});
