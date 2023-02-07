from datetime import datetime
from os import name
from flask import current_app as app
from flask_login import current_user

class Seller:
    def __init__(self, uid):
        self.uid = uid


    @staticmethod
    def seller_verify(uid):
        rows = app.db.execute('''
            SELECT *
            FROM Seller
            WHERE id=:uid
        ''',
        uid=uid
        )
        if rows:
            return True
        else:
            return False

    @staticmethod
    def become_seller(id):
        try:
            sid = app.db.execute('''
            INSERT INTO Seller(id)
            VALUES(:id)
            RETURNING id
            ''',
            id=id)
        except:
            return False

        return sid
