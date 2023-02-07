from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, amount, isSeller, address=None):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.amount = amount
        self.address = address
        self.isSeller = isSeller

    @staticmethod
    # authenticates user login by searching by email and matching the password
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, amount, is_seller, address
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    # checks if the email exists
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    # inserts new user into Users table
    def register(email, password, firstname, lastname, address):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname, address, is_seller, amount)
VALUES(:email, :password, :firstname, :lastname, :address, 0, 0)
RETURNING id
""",
                                  email=email, address=address,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            return None

    @staticmethod
    # loads user
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, firstname, lastname, amount, is_seller, address
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None

    @staticmethod
    # gets all user ids from the Users table
    def get_all_uids():
        rows = app.db.execute('''
SELECT id
FROM Users
''')
        return rows if rows else None

    @staticmethod
    # updates Users table to change a user to a seller
    def become_seller(id):
        try:
            sid = app.db.execute('''
            UPDATE Users
            SET is_seller = 1
            WHERE id = :id
            RETURNING id
            ''',
            id=id)
        except:
            return False
        return sid

    @staticmethod
    # get deposits and withdrawals history for a user
    def get_user_depo_with_acct_hist(uid):
        rows = app.db.execute('''
SELECT *
FROM depo_with_acct_hist
WHERE uid = :uid  
ORDER BY time_stamp DESC
''', uid=uid)
        return rows if rows else None

    @staticmethod
    # get order history for a user
    def get_user_orders_acct_hist(uid):
        rows = app.db.execute('''
SELECT *
FROM order_acct_hist
WHERE uid = :uid
ORDER BY time_stamp DESC
''', uid=uid)
        return rows if rows else None

    @staticmethod
    # get deposits, withdrawals, and order history for a user
    def get_user_combined_acct_hist(uid):
        rows = app.db.execute('''
SELECT *
FROM combined_acct_hist
WHERE uid = :uid
ORDER BY time_stamp DESC
''', uid=uid)
        return rows if rows else None

    @staticmethod
    # get products sold history for a user
    def get_sell_acct_hist(uid):
        rows = app.db.execute('''
SELECT *
FROM sell_acct_hist
WHERE uid = :uid
ORDER BY time_stamp DESC
''', uid=uid)
        return rows if rows else None

    @staticmethod
    # gets products sold history as well as both or one of deposits/withdrawals history and order history
    def get_user_sold_acct_hist(uid, subset):
        # must be careful with string formatting because it can lead to SQL injection weakness
        # prevents SQL injection by making sure what is inserted through string formatting is one of the valid view options below
        if subset not in ["order_acct_hist", "depo_with_acct_hist", "combined_acct_hist"]:
            return None
        rows = app.db.execute(f'''
(SELECT *
FROM {subset}
WHERE uid = :uid)
UNION
(SELECT *
FROM sell_acct_hist
WHERE uid = :uid)
ORDER BY time_stamp DESC
''', uid=uid)
        return rows if rows else None

# deposit and withdraw funds for a user
    @staticmethod
    def depo_with(uid, amount, time_stamp):
        rows = app.db.execute('''
INSERT INTO Account_History (uid, amount, time_stamp)
VALUES (:uid, :amount, :time_stamp)
''', uid=uid, amount=amount, time_stamp=time_stamp)
        return rows if rows else None

    @staticmethod
    # gets the user balance of a user by user id
    def get_user_balance(uid):
        rows = app.db.execute('''
SELECT amount
FROM Users
WHERE id = :uid
''', uid=uid)
        return rows

    @staticmethod
    # update first name
    def update_firstname(uid, firstname):
        try:
            rows = app.db.execute('''
UPDATE Users
SET firstname = :firstname
WHERE id = :uid
''', uid=uid, firstname=firstname)
            return ""
        except Exception as e:
            print(str(e))
            return str(e)

    @staticmethod
    # update last name
    def update_lastname(uid, lastname):
        try:
            rows = app.db.execute('''
UPDATE Users
SET lastname = :lastname
WHERE id = :uid
''', uid=uid, lastname=lastname)
            return ""
        except Exception as e:
            print(str(e))
            return str(e)

    @staticmethod
    # update address
    def update_address(uid, address):
        try:
            rows = app.db.execute('''
UPDATE Users
SET address = :address
WHERE id = :uid
''', uid=uid, address=address)
            return ""
        except Exception as e:
            print(str(e))
            return str(e)

    @staticmethod
    # change is_seller value
    def update_is_seller(uid, seller_val):
        try:
            rows = app.db.execute('''
UPDATE Users
SET is_seller = :seller_val
WHERE id = :uid
''', uid=uid, seller_val = seller_val)
            return ""
        except Exception as e:
            print(str(e))
            return str(e)

    @staticmethod
    # update password, including function to generate password hash
    def update_password(uid, password):
        try:
            rows = app.db.execute('''
UPDATE Users
SET password = :password
WHERE id = :uid
''', uid=uid, password=generate_password_hash(password))
            return ""
        except Exception as e:
            print(str(e))
            return str(e)

    @staticmethod
    # DEPRECIATED: tried to create a function to update any account information, but it didn't really work
    def update_non_email(uid, field, field_val):
        if field == "password":
            field_val = generate_password_hash(field_val)
        rows = app.db.execute('''
UPDATE Users
SET :field = :field_val
WHERE id = :uid
''', uid=uid, field=field, field_val = field_val)
        return rows

    @staticmethod
    # update email - raises exception if there is a duplicate email
    def update_email(uid, email):
        try:
            rows = app.db.execute("""
UPDATE Users
SET email = :email
WHERE id = :uid
""",
                                  uid=uid, email=email)
            return ""
        except Exception as e:
            print(str(e))
            return str(e)

    @staticmethod
    # get all user data by user id
    def get_all_uid_data(id):
        rows = app.db.execute("""
SELECT *
FROM Users
WHERE id = :id
""",
                              id=id)
        return rows if rows else None

    @staticmethod
    # get all data by user email
    # I think this is a duplicate of the get_data_by_email function below but I'm too scared to delete it
    def get_all_email_data(email):
        rows = app.db.execute("""
SELECT *
FROM Users
WHERE email = :email
""",
                              email=email)
        return rows if rows else None

    @staticmethod
    # get the user name of a user with the given user id
    def get_name(uid):
        rows = app.db.execute("""
SELECT firstname, lastname
FROM Users
WHERE id = :uid""", uid=uid)
        return rows if rows else None

    @staticmethod
    # get all data by user email
    def get_data_by_email(email):
        rows = app.db.execute("""
SELECT *
FROM Users
WHERE email = :email""", email=email)
        return rows if rows else None

    @staticmethod
    # get all data by user name
    # searches to see if the string is in either the first name, last name, or full name
    def get_data_by_name(sim_str):
        sim_str = '%' + sim_str.lower() + '%'
        rows = app.db.execute("""
SELECT *
FROM Users
WHERE (LOWER(firstname) LIKE :sim_str OR LOWER(lastname) LIKE :sim_str OR LOWER(CONCAT(firstname, ' ', lastname)) LIKE :sim_str)""", sim_str=sim_str)
        return rows if rows else None


