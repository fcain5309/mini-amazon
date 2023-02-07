/* Adding a user withdrawal or deposit - automatically update user account balance */

CREATE OR REPLACE FUNCTION add_acct_balance()
  RETURNS trigger AS
$$
BEGIN
    UPDATE Users
    SET amount = amount + NEW.amount
    WHERE id = NEW.uid;
RETURN NEW;
END;
$$
LANGUAGE 'plpgsql';

DROP TRIGGER IF EXISTS user_new_depo_with ON Account_History;

CREATE TRIGGER user_new_depo_with
AFTER INSERT ON Account_History
FOR EACH ROW
EXECUTE PROCEDURE add_acct_balance();

/* Submitting an order - subtracting the total price from the buyer's account balance */

CREATE OR REPLACE FUNCTION add_order_balance()
  RETURNS trigger AS
$$
BEGIN
    UPDATE Users
    SET amount = amount - NEW.total_price
    WHERE id = NEW.uid;
RETURN NEW;
END;
$$
LANGUAGE 'plpgsql';

DROP TRIGGER IF EXISTS user_new_order ON Specific_Order;

CREATE TRIGGER user_order
AFTER INSERT ON Specific_Order
FOR EACH ROW
EXECUTE PROCEDURE add_order_balance();

/* Submitting an order - adding the order contents revenue to the seller's account */

CREATE OR REPLACE FUNCTION update_balance_seller()
  RETURNS trigger AS
$$
BEGIN
    UPDATE Users
    SET amount = amount + (NEW.quantity * NEW.price)
    WHERE id IN (SELECT Inventory.uid
    FROM Inventory
    WHERE Inventory.id = NEW.inventory_id);
RETURN NEW;
END;
$$
LANGUAGE 'plpgsql';

DROP TRIGGER IF EXISTS seller_order_content_balance ON Order_Content;

CREATE TRIGGER seller_order_content_balance
AFTER INSERT ON Order_Content
FOR EACH ROW
EXECUTE PROCEDURE update_balance_seller();