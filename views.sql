-- sums up the deposits and withdrawals for a specific user
CREATE VIEW user_acct_hist_sum AS
SELECT uid, SUM(amount) AS total_depo_with
FROM Account_History
GROUP BY uid;

-- look at specific orders made by a specific user id
CREATE VIEW user_order_sum AS
SELECT uid, SUM(total_price) AS total_order_amount
FROM Specific_Order
GROUP BY uid;

-- view deposit and withdrawal account history
CREATE VIEW depo_with_acct_hist AS
SELECT uid, amount, time_stamp,
    CASE
        WHEN amount >= 0 THEN 'Deposit'
        ELSE 'Withdrawal'
    END
    AS transact_type, CAST(NULL AS int) AS order_id
FROM Account_History;

-- view the purchased history of a user
CREATE VIEW order_acct_hist AS
SELECT uid, -1 * total_price AS amount, time_stamp, 'Purchased Order' AS transact_type, id as order_id
FROM Specific_Order;

-- view the transactions seller made, grouping order contents ino the same order
CREATE VIEW sell_acct_hist AS
SELECT Inventory.uid AS uid, SUM(Order_Content.price * Order_Content.quantity) as amount, Specific_Order.time_stamp, 'Sold Products' AS transact_type, Specific_Order.id AS order_id
FROM Order_Content
JOIN Specific_Order
ON (Specific_Order.id = Order_Content.order_id)
JOIN Inventory
ON (Inventory.id = Order_Content.inventory_id)
GROUP BY Specific_Order.id, Inventory.uid;

-- view the user's history including deposits, withdrawals, and purchase orders
CREATE VIEW combined_acct_hist AS
SELECT uid, amount, time_stamp,
    CASE
        WHEN amount >= 0 THEN 'Deposit'
        ELSE 'Withdrawal'
    END
    AS transact_type, NULL as order_id
FROM Account_History
UNION ALL
SELECT uid, -1 * total_price AS amount, time_stamp, 'Order' AS transact_type, id as order_id
FROM Specific_Order;

-- view to calculate the account balance of a user, thought this is usually unnecessary
CREATE VIEW calc_acct_balance AS
SELECT uid, SUM(amount) as amount
FROM combined_acct_hist
GROUP BY uid;