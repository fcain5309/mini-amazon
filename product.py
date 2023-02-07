from flask import current_app as app


class Product:
    def __init__(self, id, name, category, description, price, image, review=None, quantity=None):
        self.id = id
        self.name = name
        self.category = category
        self.description = description
        self.price = price
        self.image = image
        self.review = review
        self.quantity = quantity

    # get all product info for one product by id
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT p.*, r.review_content
FROM Products p
LEFT JOIN Product_Review r
ON p.id = r.pid
WHERE p.id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    # get all info for one product by product name
    @staticmethod
    def get_by_name(name):
        rows = app.db.execute('''
SELECT p.*
FROM Products p
WHERE LOWER(p.name) = LOWER(name)
''',
                              name=name)
        if rows is None:
            return None
        else:
            return Product(*(rows[0]))

    # check whether a given product exists by querying with name
    @staticmethod
    def validate_product(name):
        rows = app.db.execute('''
SELECT p.*
FROM Products p
WHERE p.name = :name
''',
                              name=name)
        if rows:
            return False
        else:
            return True

    # add a new product by inserting into Products table-- no ability to add image
    @staticmethod
    def add_new_product(name, category, description, price):
        try:
            rows = app.db.execute("""
INSERT INTO Products(name, category, description, price)
VALUES(:name, :category, :description, :price)
RETURNING id
""",
                                  name=name,
                                  category=category,
                                  description=description,
                                  price=price)
            id = rows[0][0]
            return id
        except Exception as e:
            print(str(e))
            return None

    # get all products sold by a particular seller (uid) AND are active inventory
    @staticmethod
    def get_active_seller_prods(uid):
        rows = app.db.execute('''
SELECT p.*, i.uid, i.quantity
FROM Products p
LEFT JOIN Inventory i
ON p.id = i.pid
WHERE i.uid = :uid AND p.id IN (SELECT pid
                FROM Inventory
                WHERE uid = :uid
                AND is_active = 1)
''',
                              uid = uid)
        return [Product(*row) for row in rows]

    # get all products sold by a particular seller (uid) AND are inactive inventory
    @staticmethod
    def get_inactive_seller_prods(uid):
        rows = app.db.execute('''
SELECT p.*, i.uid, i.quantity
FROM Products p
LEFT JOIN Inventory i
ON p.id = i.pid
WHERE i.uid = :uid AND p.id IN (SELECT pid
                FROM Inventory
                WHERE uid = :uid
                AND is_active = 0)
''',
                              uid = uid)
        return [Product(*row) for row in rows]

    # update a product by changing product name, category, description, or price
    @staticmethod
    def update_product(pid, name, category, description, price):
        rows = app.db.execute('''
            UPDATE Products
            SET name = :name, category = :category, description = :description, price = :price
            WHERE id = :pid
        ''',
                              pid=pid,
                              name=name,
                              category=category,
                              description=description,
                              price=price)
        if rows:
            return True
        else:
            return False

    # get product info + review info for all products
    @staticmethod
    def get_all(offset=0, per_page=0):
        rows = app.db.execute('''
WITH avgRating AS 
(SELECT ROUND(AVG(pr.review_content), 1) avgrev, pr.pid
FROM Product_Review pr
GROUP BY pr.pid)
SELECT p.*, r.avgrev
FROM Products p 
LEFT JOIN avgRating r 
ON p.id = r.pid
''')    
        if per_page == 0:
            return [Product(*row) for row in rows]
        else:
            products = rows[offset: offset+per_page]
            return [Product(*product) for product in products], len(rows)

    # get product info for all products that fall under certain price range
    @staticmethod
    def get_by_price(pr, offset=0, per_page=0):
        rows = app.db.execute('''
WITH avgRating AS 
(SELECT ROUND(AVG(pr.review_content), 1) avgrev, pr.pid
FROM Product_Review pr
GROUP BY pr.pid)
SELECT p.*, r.avgrev 
FROM Products p 
LEFT JOIN avgRating r 
ON p.id = r.pid
WHERE p.price <= :pr
ORDER BY price DESC
''',
                            pr=pr)
        if per_page == 0:
            return [Product(*row) for row in rows]
        else:
            products = rows[offset: offset+per_page]
            return [Product(*product) for product in products], len(rows)

    # get product info for all products that match certain category
    @staticmethod
    def get_by_category(cat, offset=0, per_page=0):
        rows = app.db.execute("""
WITH avgRating AS 
(SELECT ROUND(AVG(pr.review_content), 1) avgrev, pr.pid
FROM Product_Review pr
GROUP BY pr.pid)
SELECT p.*, r.avgrev 
FROM Products p
LEFT JOIN avgRating r 
ON p.id = r.pid
WHERE LOWER(p.category) LIKE LOWER('%{}%')
""".format(cat),
                            cat=cat)
        if per_page == 0:
            return [Product(*row) for row in rows]
        else:
            products = rows[offset: offset+per_page]
            return [Product(*product) for product in products], len(rows)

    # get product info for all products that match certain keyword
    @staticmethod
    def get_by_common_word(word, offset=0, per_page=0):
        rows = app.db.execute("""
WITH avgRating AS 
(SELECT ROUND(AVG(pr.review_content), 1) avgrev, pr.pid
FROM Product_Review pr
GROUP BY pr.pid)
SELECT p.*, r.avgrev 
FROM Products p
LEFT JOIN avgRating r 
ON p.id = r.pid
WHERE LOWER(p.description) LIKE LOWER('%{}%') 
OR LOWER(p.name) LIKE LOWER('%{}%')
""".format(word, word),
                            word=word)
        if per_page == 0:
            return [Product(*row) for row in rows]
        else:
            products = rows[offset: offset+per_page]
            return [Product(*product) for product in products], len(rows)
