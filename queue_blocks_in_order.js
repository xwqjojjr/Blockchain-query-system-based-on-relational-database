var amqp = require('amqp');
//var BigNumber = require("bignumber.js");
var winston = require("winston");
var Web3 = require("web3");
// 连接到以太坊节点
var web3 = new Web3();


web3.setProvider(new Web3.providers.HttpProvider("http://localhost:8545"));
if(!web3.currentProvider)
        console.log("No currentProvider");
else
        console.log("Get currentProvider~");


var	 BLOCK_REWARD		 = 5,
	 FIRST_BLOCK		 = 0,
	 MAXIMUM_BLOCK		 = 1000000,
	 REPORT_FREQUENCY_BLOCKS = 1800;


console.log("MAX_BLOCK=" +  MAXIMUM_BLOCK)

var connection = amqp.createConnection({ 'host': 'localhost' });
console.log(connection)


var queue_blocks_from = function (block_number) {
	web3.eth.getBlock(block_number, true, function(error, result) {
		if(error) {
			console.log("error", "Error getting block number: " + block_number + ". '" + error + "'");
		} else {
			if(result){
		console.log("info", "Queueing Block #" + block_number + " (with " + result.transactions.length + " transactions).");
				if(block_number % REPORT_FREQUENCY_BLOCKS == 0){ 
					console.log("info", "Queueing Block #" + block_number + " (with " + result.transactions.length + " transactions).");
				}
				connection.publish("ethblocks", result);
			} else {
				console.log("warn", "No block seen for #" + block_number);
			}
		}
		if(block_number < MAXIMUM_BLOCK){
			queue_blocks_from(block_number + 1)
		}
	});
	};



connection.on('ready', function () {
	queue_blocks_from(FIRST_BLOCK);
});
