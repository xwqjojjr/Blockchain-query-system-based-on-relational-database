var BigNumber = require("bignumber");
var Web3 = require("web3");
// 连接到以太坊节点
var web3 = new Web3();
var addr = '0xeD17Ea8E9fd42159037deE95ea173a56c54f55ce';

web3.setProvider(new Web3.providers.HttpProvider("http://localhost:8545"));
if(!web3.currentProvider)
        console.log("No currentProvider");
else
        console.log("Get currentProvider~");

web3.eth.getBalance(addr,function(error,result){
//	console.log(addr);
//	console.log(result);
	if(error) {
                        console.log("error", "Error getting block number: " + block_number + ". '" + error + "'");
                        connection.publish("error_block",block_number)
        } else {
			console.log(result)
	}	
    });
	
