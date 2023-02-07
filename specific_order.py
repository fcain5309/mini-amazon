from flask import current_app as app


class Specific_Order:
    def __init__(self, id, uid, time_stamp):
        self.id = id
        self.uid = uid
        self.time_stamp = time_stamp

    @staticmethod
    # get all data with a specific_order id
    def get(id):
        rows = app.db.execute('''
SELECT *
FROM Specific_Order
WHERE id = :id
''',
                              id=id)
        return rows if rows else None

    @staticmethod
    # get all orders made by a user id
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Specific_Order
WHERE uid = :uid
ORDER BY time_purchased DESC
''',
                              uid=uid)
        return rows if rows else None

    @staticmethod
    # get all orders made by a user id since a time
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Specific_Order
WHERE uid = :uid
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return rows if rows else None


    @staticmethod
    # sort orders made by a user by multiple possible columns, either ascending or descending
    def sort_orders_by(uid, order_column, asc_desc):
        # string formatting is usually a risky way to set up a SQL query
        # this should be hard to SQL injection attack, since the variables should come from a selection form
        # just in case, I'm going to check to make sure that order_column and asc_desc are valid column names and ASC/DESC parameters
        if asc_desc not in ["ASC", "DESC"] or order_column not in ["time_stamp", "id", "total_price", "status", "unique_items", "total_items"]:
            return None
        rows = app.db.execute(f'''
    SELECT Specific_Order.id, Specific_Order.uid, Specific_Order.time_stamp, Specific_Order.total_price, Specific_Order.status,
        COUNT(Order_Content.id) AS unique_items, SUM(Order_Content.quantity) AS total_items
    FROM Specific_Order
    JOIN Order_Content
    ON (Specific_Order.id = Order_Content.order_id)
    WHERE uid = :uid
    GROUP BY Specific_Order.id
    ORDER BY {order_column} {asc_desc}
    ''',
                                uid=uid)
        return rows if rows else None

    @staticmethod
    # sort order line items made by a user by multiple possible columns, either ascending or descending
    def sort_items_by(uid, items_column, asc_desc, sim_str):
        sim_str = '%' + sim_str.lower() + '%'
        # string formatting is usually a risky way to set up a SQL query
        # this should be hard to SQL injection attack, since the variables should come from a selection form
        # just in case, I'm going to check to make sure that order_column and asc_desc are valid column names and ASC/DESC parameters
        if asc_desc not in ["ASC", "DESC"] or items_column not in ["product_name", "product_id", "seller_firstname", "seller_lastname", "seller_uid",
            "time_stamp", "category", "price", "total_price", "quantity", "item_status", "order_id"]:
            return None
        rows = app.db.execute(f'''
    SELECT Specific_Order.id AS order_id, Specific_Order.uid, Specific_Order.time_stamp,
        Inventory.uid as seller_uid, Users.firstname as seller_firstname, Users.lastname AS seller_lastname,
        Order_Content.inventory_id, Order_Content.price, Order_Content.quantity, (Order_Content.price * Order_Content.quantity) AS total_price, Order_Content.status AS item_status,
        Products.name AS product_name, Products.category, Products.id AS product_id
    FROM Specific_Order
    JOIN Order_Content
    ON (Specific_Order.id = Order_Content.order_id)
    JOIN Inventory
    ON (Order_Content.inventory_id = Inventory.id)
    JOIN Products
    ON (Inventory.pid = Products.id)
    JOIN Users
    ON (Inventory.uid = Users.id)
    WHERE Specific_Order.uid = :uid AND (LOWER(Users.firstname) LIKE :sim_str OR LOWER(Users.lastname) LIKE :sim_str OR LOWER(CONCAT(Users.firstname, ' ', Users.lastname)) LIKE :sim_str
        OR LOWER(Products.name) LIKE :sim_str OR LOWER(Products.category) LIKE :sim_str)
    ORDER BY {items_column} {asc_desc}
    ''',
                                uid=uid, sim_str=sim_str)
        return rows if rows else None