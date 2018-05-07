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

drop table Addresses;
create table Addresses(
addr varchar(100) unique,
addr_type int,
eth bigint
);

drop table Transactions;
CREATE TABLE `Transactions` (
  `block_number` int(11) DEFAULT NULL,
  `block_hash` varchar(100) DEFAULT NULL,
  `tx_from` varchar(100) DEFAULT NULL,
  `tx_hash` varchar(100) DEFAULT NULL,
  `tx_index` int(11) DEFAULT NULL,
  `tx_input` varchar(10000) DEFAULT NULL,
  `tx_value` varchar(100) DEFAULT NULL,
  `tx_type` int(11) DEFAULT NULL,
  `nonce` int(11) DEFAULT NULL,
  `tx_to` varchar(100) DEFAULT NULL
);

drop table error_block;
create table error_block(
block_number int
);

drop table Tx_From;
create table Tx_From(
addr varchar(70),
tx_hash varchar(70)
);
drop table Tx_To;
create table Tx_To(
addr varchar(70),
tx_hash varchar(70)
);

drop table Addresses;
create table Addresses(
addr varchar(100),
addr_type int,
eth bigint
);

drop table Tx_Block;
create table Tx_Block(
tx_hash varchar(70),
block_number int,
block_hash varchar(70)
);
