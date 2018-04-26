var amqp = require('amqp');
var BigNumber = require("bignumber");
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
	 FIRST_BLOCK		 = 500000,
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
				//保存交易
				var cur_tx,cur_tx_type;
				for(var i=0 ; i<result.transactions.length;i++){
					cur_tx = result.transactions[i];
					 if(cur_tx.to == null){
                                                cur_tx_type = 2; // Contract Creation
                                        } else {
                                                if(web3.eth.getCode(cur_tx.to) == "0x"){
                                                        cur_tx_type = 0; // Person to Person
                                                } else {
                                                        cur_tx_type = 1; // Person to Contract
                                                }
                                        }
                                        console.log(cur_tx,cur_tx_type)
					connection.publish("ethtx",cur_tx)
					connection.publish("ethtx",cur_tx_type)
 				}
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
