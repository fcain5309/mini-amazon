\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Account_History FROM 'Account_History.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.account_history_id_seq',
                         (SELECT MAX(id)+1 FROM Account_History),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);

\COPY Inventory FROM 'Inventory.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.inventory_id_seq',
                         (SELECT MAX(id)+1 FROM Inventory),
                         false);

\COPY Cart FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.cart_id_seq',
                         (SELECT MAX(id)+1 FROM Cart),
                         false);

\COPY Specific_Order FROM 'Specific_Order.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.specific_order_id_seq',
                         (SELECT MAX(id)+1 FROM Specific_Order),
                         false);

\COPY Order_Content FROM 'Order_Content.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.order_content_id_seq',
                         (SELECT MAX(id)+1 FROM Order_Content),
                         false);

\COPY Product_Review FROM 'Product_Review.csv' WITH DELIMITER ',' NULL '' CSV;
SELECT pg_catalog.setval('public.product_review_id_seq',
                         (SELECT MAX(id)+1 FROM Product_Review),
                         false);

\COPY Seller_Review FROM 'Seller_Review.csv' WITH DELIMITER ',' NULL '' CSV;
SELECT pg_catalog.setval('public.seller_review_id_seq',
                         (SELECT MAX(id)+1 FROM Seller_Review),
                         false);
