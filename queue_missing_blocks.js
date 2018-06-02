var amqp = require('amqp');
var Web3 = require("web3");
//var BigNumber = require("bignumber.js");
var mysql = require('mysql2');

var winston = require("winston");
var cursor = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password:'63982677',
  database: 'ethereum'
});


var RPC_SERVER = "http://localhost:8545";

var web3 = new Web3(new Web3.providers.HttpProvider(RPC_SERVER));


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
        };


connection.on('ready', function () {
	winston.log("info", "Rabbit Connection ready, starting to queue...");
	missing = [];
	var query = cursor.query("SELECT blockNumber from EthTest_errorblock",
			function(err, result){
				result.forEach(function(row) {
					//console.log(row.blockNumber);
					missing.push(row.blockNumber);
				});
				var repeat_queue_blocks = function(){
					console.log("info", missing.length + " remaining...");

					if(missing.length){
						for(var i = 0; i < 500; i++){
							queue_block(missing.pop());
						}
						setTimeout(repeat_queue_blocks, 1100);
					}
				};
				console.log("info", "Starting to queue blocks in 6 seconds");
				console.log("info", missing.length + " remaining...");
				setTimeout(repeat_queue_blocks.bind(this, 0), 6000);
			});

});


winston.log("info", "Done!");
