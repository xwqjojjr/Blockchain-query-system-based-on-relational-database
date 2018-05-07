drop table Blocks;
create table Blocks(
block_number int,
block_hash varchar(100),
timestamp varchar(100),
prev_block_hash varchar(100),
nonce varchar(100),
miner_addr varchar(100),
difficulty bigint,
size_bytes int,
extra_data varchar(2000)
);


create table Addresses(
Address varchar(100) unique,
Address_type int,
eth bigint
);

CREATE TABLE `Transactions` (
  `block_number` int(11) DEFAULT NULL,
  `block_hash` varchar(100) DEFAULT NULL,
  `tx_from` varchar(100) DEFAULT NULL,
  `tx_hash` varchar(100) DEFAULT NULL,
  `tx_index` int(11) DEFAULT NULL,
  `tx_input` varchar(2000) DEFAULT NULL,
  `tx_value` varchar(100) DEFAULT NULL,
  `tx_type` int(11) DEFAULT NULL,
  `nonce` int(11) DEFAULT NULL,
  `tx_to` varchar(100) DEFAULT NULL
);

create table error_block(
block_number int;
);
