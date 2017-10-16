drop table if exists customers;
create table customers (
	id integer primary key autoincrement,
	name char not null,
	phone char,
	status char not null,
	type char not null,
	b_day Date,
	abo_number char,
	join_date Date,
	family text,
	occupation text,
	rescreation text,
	financial text,
	achievement text
);

drop table if exists customer_progress;
create table customer_progress (
	id integer primary key,
	cid integer not null,
	progress_date Date not null,
	progress_type char not null,
	progress_info text
)

