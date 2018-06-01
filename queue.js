var amqp = require('amqp');
var Web3 = require("web3");
//var BigNumber = require("bignumber.js");
var winston = require("winston");


var RPC_SERVER = "http://localhost:8545";

var web3 = new Web3(new Web3.providers.HttpProvider(RPC_SERVER));

var	BLOCK_REWARD = 5,
	FIRST_BLOCK = 1,
	MAXIMUM_BLOCK = 1000000,	
//	MAXIMUM_BLOCK = web3.eth.blockNumber,
	BLOCKS_AT_A_TIME = 1800,
	BLOCK_QUEUE_TIMEOUT = 2000;
console.log(FIRST_BLOCK,MAXIMUM_BLOCK)

if(!web3.isConnected()){
	console.log("error", "web3 is not connected to the RPC");
	process.exit(1);
}
var connection = amqp.createConnection({ 'host': 'localhost' });
console.log(connection)
var queue_block = function (block_number){
	web3.eth.getBlock(block_number, true, function(error, result) {
		if(error) {
			console.log("error", "Error getting block number: " + block_number + ". '" + error + "'");
			connection.publish("error_block",block_number)
		} else {
			if(result){
				//console.log(result)
				//保存交易
				var cur_tx,cur_tx_type;
				for(var i=0 ; i<result.transactions.length;i++){
					cur_tx = result.transactions[i];
					connection.publish("ethtx",cur_tx)
 				}
				//console.log("info", "Queueing Block #" + block_number + " (with " + result.transactions.length + " transactions).");
				connection.publish("ethblocks", result);
			} else {
				console.log("warn", "No block seen for #" + block_number);
			}
		}
	});
	},
	queue_n_blocks = function(starting_block, n) {
		console.log("info", "Queueing " + n + " blocks, from " + starting_block);
		for(var i = starting_block; i < (starting_block + n); i++){
				queue_block(i);
		}
	};



connection.on('ready', function () {
	console.log("info", "Rabbit Connection ready, starting queueing in " + BLOCK_QUEUE_TIMEOUT/1000 + "s");
	var repeat_queue_blocks = function(current_block) {
		if(current_block <= MAXIMUM_BLOCK){
			queue_n_blocks(current_block, BLOCKS_AT_A_TIME);
			current_block = current_block+BLOCKS_AT_A_TIME;
			setTimeout(repeat_queue_blocks.bind(this, (current_block)), BLOCK_QUEUE_TIMEOUT)
		}
	};
	setTimeout(repeat_queue_blocks.bind(this, FIRST_BLOCK), BLOCK_QUEUE_TIMEOUT);
});
