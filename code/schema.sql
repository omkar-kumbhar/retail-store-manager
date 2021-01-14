-- drop table if exists Offices;
drop table if exists offices cascade;
create table Offices(
	office_code varchar(64) primary key,
	office_name varchar(128) not null,
	phone varchar not null
);
drop table if exists office_Addresses cascade;
create table Office_addresses(
	office_address varchar(128) primary key,
	city varchar(64),
	stat varchar(128),
	country varchar(128),
	postal_code varchar(32),
	office_code varchar(64) not null,
	foreign key (office_code) references Offices(office_code)
);


drop table if exists employees cascade;
create table Employees(
	employee_number integer primary key,
	lastname varchar(64) not null,
	firstname varchar(64) not null,
	email varchar(64) unique not null,
	office_code varchar(64) not null,
	job_title varchar(64) not null,
	foreign key (office_code) references Offices(office_code)
);

drop table if exists products cascade;
create table Products(
	product_code varchar(64) primary key,
	product_name varchar(64) not null,
	product_categories varchar(64) not null,
	product_description varchar(64) not null,
	selling_price varchar(64) not null 
);

drop table if exists customers cascade;
create table Customers(
	customer_number integer primary key,
	firstname varchar(128) not null,
	lastname varchar(128) not null,
	phone varchar(64) unique not null,
	foreign key(sales_representative) references Employees(employee_number)
);

drop table if exists inventory cascade;
create table Inventory(
	product_code varchar(64),
	office_code varchar(64),
	quantity integer not null,
	primary key(product_code,office_code),
	foreign key(product_code) references Products(product_code),
	foreign key(office_code) references Offices(office_code)
);

drop table if exists customer_addresses cascade;
create table Customer_Addresses(
	customer_address varchar(128) primary key,
	city varchar(64) not null,
	state varchar(128) not null,
	country varchar(128) not null,
	postal_code varchar(32) not null,
	customer_number integer not null,
	foreign key(customer_number) references Customers(customer_number)
);

drop table if exists orders cascade;
create table Orders(
	order_number int primary key,
	order_date date not null,
	shipped_date date not null,
	customer_number integer not null,
	foreign key (customer_number) references Customers(customer_number)
);

drop table if exists order_Details cascade;
create table Order_Details(
	order_number integer,
	product_code varchar(32),
	office_code varchar(64),
	quantity integer not null,
	price decimal not null,
	primary key(order_number,product_code),
	foreign key (order_number) references Orders(order_number),
	foreign key (product_code) references Products(product_code),
	foreign key (office_code) references Offices(office_code)
);

drop table if exists payments cascade;
create table Payments(
	customer_number integer,
	order_number integer,
	payment_date date not null,
	amount decimal not null,
	primary key(order_number),
	foreign key (customer_number) references Customers(customer_number),
	foreign key (order_number) references Orders(order_number)
);

