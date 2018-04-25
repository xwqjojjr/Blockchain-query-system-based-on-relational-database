psql -U blockchains -d db_blockchains -h 127.0.0.1 -p 5432

INSERT INTO ethereum.Blocks
          (block_number, block_hash, timestamp, prev_block_hash, nonce, miner_addr, difficulty, size_bytes, extra_data, block_reward)
          VALUES (%(number)s, %(hash)s, to_timestamp(%(timestamp)s), %(parentHash)s, %(nonce)s, %(miner)s, %(difficulty)s, %(size)s, %(extraData)s, 5

drop table Blocks;
create table Blocks(
block_number int,
block_hash varchar(100),
timestamp datetime,
prev_block_hash varchar(100),
nonce varchar(100),
miner_addr varchar(100),
difficulty bigint,
size_bytes int,
extra_data varchar(2000)
);

drop table Blocks;
create table Blocks(
block_hash varchar(100)
);

INSERT INTO Addresses
                  (address, address_type)
                  VALUES (%s, %s)


create table Addresses(
address varchar (100),
address_type int
);


INSERT INTO Addresses_Blocks
                  (address, block_hash)
                  VALUES (%s, %s)

create table Addresses_Blocks(
address varchar(100),
block_hash varchar(100)
);

INSERT INTO ethereum.Transactions
            (tx_hash, tx_index, input, tx_type, nonce)
            VALUES (%(hash)s, %(transactionIndex)s, %(input)s, %(tx_type)s, %(nonce)s)

create table Transactions(
tx_hash varchar(100),
tx_index int,
input varchar(200),
tx_type int,
nonce int
);

INSERT INTO TxFromAddress
            (address, tx_hash, input_value)
            VALUES (%(from)s, %(hash)s, %(value)s)

create table TxFromAddress(
address varchar(100),
tx_hash varchar(100),
input_value varchar(1000)
);

INSERT INTO TxToAddress
            (address, tx_hash, output_value)
            VALUES (%(to)s, %(hash)s, %(value)s)


create table TxToAddress(
address varchar(100),
tx_hash varchar(100),
output_value varchar(1000)
);


INSERT INTO ethereum.Transactions_Blocks
            (tx_hash, block_hash)
            VALUES (%(tx)s, %(block)s)


create table Transactions_Blocks(
tx_hash varchar(100),
block_hash varchar(100)
);
