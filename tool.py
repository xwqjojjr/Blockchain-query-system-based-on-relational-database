import sha3
import rlp
import binascii
#求智能合约地址
#发送地址+nonce进行rlp编码，再用keccak_256哈希计算，保留后160位，再转化为2进制
sha3.keccak_256(rlp.encode([binascii.unhexlify("b100987e77feba6f022dbd22b80b008e35d3ff2e"),0])).hexdigest()[-40:]
class Helper(object):

    def calculate_contract_address(self, tx=None, from_nonce_tuple=None):
        if tx: 
            from_address = tx["from"]
            nonce = tx["nonce"]
        elif from_nonce_tuple:
            from_address = from_nonce_tuple[0]
            nonce = from_nonce_tuple[1] 
    
        return "0x" + sha3.keccak_256(rlp.encode([binascii.unhexlify(from_address[2:]),nonce])).hexdigest()[-40:]

