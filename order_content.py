from flask import current_app as app
from .specific_order import Specific_Order

class Order_Content:
    def __init__(self, id, order_id, inventory_id, quantity, price):
        self.id = id
        self.order_id = order_id
        self.inventory_id = inventory_id
        self.quantity = quantity
        self.price = price

    @staticmethod
    # get all order_content data with a certain id
    def get(id):
        rows = app.db.execute('''
SELECT *
FROM Order_Content
WHERE id = :id
''',
                              id=id)
        return rows if rows else None

    @staticmethod
    # get all order contents bought by a specific user
    def get_all_by_uid(uid):
        rows = app.db.execute('''
WITH join_order_contents
AS (SELECT order_id, Specific_Order.uid AS uid, time_stamp, Inventory.uid AS seller_uid, name, Order_Content.quantity, Order_Content.price 
FROM Order_Content
INNER JOIN Specific_Order
ON (Order_Content.order_id = Specific_Order.id)
INNER JOIN Inventory
ON (Inventory.id = Order_Content.inventory_id)
INNER JOIN Products
ON (Inventory.pid = Products.id))
SELECT *
FROM join_order_contents
WHERE (join_order_contents.uid = :uid)
ORDER BY time_stamp DESC
''',
                              uid=uid)
        return rows if rows else None

    @staticmethod
    # get all order contents bought by a specific user since a certain time
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
WITH join_order_contents
AS (SELECT order_id, uid, time_stamp, Order_Content.id, inventory_id, quantity, price
FROM Order_Content
INNER JOIN Specific_Order
ON (Order_Content.order_id = Specific_Order.id))
SELECT *
FROM join_order_contents
WHERE (join_order_contents.uid = :uid
AND join_order_contents.time_stamp >= :since)
ORDER BY time_stamp DESC
''',
                              uid=uid,
                              since=since)
        return rows if rows else None

    @staticmethod
    # get all order contents from a particular order
    def get_all_by_order_id(order_id):
        rows = app.db.execute('''
SELECT order_id, uid, time_stamp, Order_Content.id, inventory_id, quantity, price
FROM Order_Content
INNER JOIN Specific_Order
ON (Order_Content.order_id = Specific_Order.id)
WHERE (Order_Content.order_id = :order_id)
''',
                              order_id=order_id)
        return rows if rows else None

    @staticmethod
    # get all order contents which buy/sell a particular inventory (product and seller)
    def get_all_by_inventory_id(inventory_id):
        rows = app.db.execute('''
WITH join_order_contents
AS (SELECT order_id, Specific_Order.uid AS uid, time_stamp, Inventory.uid AS seller_uid, name, Order_Content.quantity, Order_Content.price
FROM Order_Content
INNER JOIN Specific_Order
ON (Order_Content.order_id = Specific_Order.id)
INNER JOIN Inventory
ON (Inventory.id = Order_Content.inventory_id)
INNER JOIN Products
ON (Inventory.pid = Products.id))
SELECT *
FROM join_order_contents
WHERE (join_order_contents.inventory_id = :inventory_id)
ORDER BY time_stamp DESC
''',
                              inventory_id=inventory_id)
        return rows if rows else None

    @staticmethod
    # get all order contents sold by a particular user
    def get_all_by_sid(uid):
        rows = app.db.execute('''
WITH join_order_contents
AS (SELECT order_id, Specific_Order.uid AS uid, time_stamp, Inventory.uid AS seller_uid, Inventory.id AS inventory_id, name, Order_Content.quantity, Order_Content.price, address, total_price, Order_Content.status as fulfillment_status, Users.firstname as firstname, Users.lastname as lastname
FROM Order_Content
INNER JOIN Specific_Order
ON (Order_Content.order_id = Specific_Order.id)
INNER JOIN Inventory
ON (Inventory.id = Order_Content.inventory_id)
INNER JOIN Products
ON (Inventory.pid = Products.id)
INNER JOIN Users
ON (Specific_Order.uid = Users.id))
SELECT *
FROM join_order_contents
WHERE (join_order_contents.seller_uid = :uid)
ORDER BY time_stamp DESC
''',
                              uid=uid)
        return rows if rows else None

    @staticmethod
    # change fulfillment of a specific order by changing status
    def change_fulfillment(oid, inventory_id, status):
        rows = app.db.execute('''
            UPDATE Order_Content
            SET status = :status
            WHERE order_id = :oid
            AND inventory_id = :inventory_id
        ''',
                              oid=oid,
                              inventory_id=inventory_id,
                              status=status)
        if rows:
            return True
        else:
            return False