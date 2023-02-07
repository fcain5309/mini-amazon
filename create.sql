-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.

CREATE TABLE Users (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_seller INT NOT NULL,
    amount DECIMAL(12,2) NOT NULL
);

CREATE TABLE Account_History (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    time_stamp timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'EST'),
    FOREIGN KEY (uid) REFERENCES Users(id),
    CONSTRAINT Account_History_Keys UNIQUE (uid, time_stamp)
);

CREATE TABLE Products (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(80) NOT NULL,
    description VARCHAR(500) NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    image VARCHAR(800)
);
 
CREATE TABLE Inventory (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL,
    pid INT NOT NULL,
    quantity INT NOT NULL,
    is_active INT NOT NULL,
    FOREIGN KEY (uid) REFERENCES Users(id),
    FOREIGN KEY (pid) REFERENCES Products(id),
    CONSTRAINT Inventory_Keys UNIQUE (uid, pid)
);

CREATE TABLE Specific_Order ( 
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL,
    time_stamp timestamp without time zone NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    status VARCHAR(80) NOT NULL,
    FOREIGN KEY (uid) REFERENCES Users(id),
    CONSTRAINT Specific_Order_Keys UNIQUE (uid, time_stamp)
);

CREATE TABLE Cart (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    buy_uid INT NOT NULL REFERENCES Users(id),
    sell_uid INT NOT NULL REFERENCES Users(id),
    inventory_id INT NOT NULL REFERENCES Inventory(id),
    pid INT NOT NULL REFERENCES Products(id),
    quant INT,
    prod_status VARCHAR(255),
    CONSTRAINT Cart_Keys UNIQUE (buy_uid, inventory_id)
); 

CREATE TABLE Order_Content (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    order_id INT NOT NULL,
    inventory_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    status VARCHAR(255) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Specific_Order(id),
    FOREIGN KEY (inventory_id) REFERENCES Inventory(id),
    CONSTRAINT Order_Content_Keys UNIQUE (order_id, inventory_id)
);

CREATE TABLE Product_Review (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    review_time timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    review_content INT NOT NULL,
    CONSTRAINT Product_Review_Keys UNIQUE (uid, pid)
);

CREATE TABLE Seller_Review (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL REFERENCES Users(id),
    uid2 INT NOT NULL REFERENCES Users(id),
    review_time timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    review_content INT NOT NULL,
    CONSTRAINT Seller_Review_Keys UNIQUE (uid, uid2)
);
