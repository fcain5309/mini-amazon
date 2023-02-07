from flask import render_template, request
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField
from wtforms.validators import DataRequired, Optional, NumberRange
from flask_paginate import Pagination, get_page_parameter, get_page_args
from flask_login import current_user
from .models.product import Product
from .models.review import Product_Review
from .models.inventory import Inventory
from .models.cart import Cart


from flask import Blueprint
bp = Blueprint('products', __name__)

# form for executing filters on product browse page
class FilterForm(FlaskForm):
    max_price = IntegerField('Filter by Price', validators=[Optional()])
    category = StringField('Filter by Category', validators=[Optional()])
    keyword = StringField('Filter by Keyword', validators=[Optional()])
    submit = SubmitField('Filter')

# form for adding to cart
class addToCart(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0, message="Quantity should > 0")])
    submit = SubmitField('Add to Cart')


# displays all products with pagination after a search from the search bar-- has ability to filter all products
@bp.route('/products/<search>', methods=['GET', 'POST'])
def search(search):
    page, per_page, offset = get_page_args(page_parameter='page',
                                        per_page_parameter='per_page') # pagination variables

    products, total = Product.get_by_common_word(search, offset=offset, per_page=per_page)
    form = FilterForm()
    p = form.max_price.data # price
    c = form.category.data # category
    kw = form.keyword.data # keyword
    if form.validate_on_submit():
        # determine which filter should be applied and run appropriate query
        if p:
            products, total = Product.get_by_price(p, offset=offset, per_page=per_page)
        elif c:
            products, total = Product.get_by_category(c, offset=offset, per_page=per_page)
        else:
            products, total = Product.get_by_common_word(kw, offset=offset, per_page=per_page)

    pagination = Pagination(page=page, per_page=per_page, total=total, show_single_page=True)

    return render_template('filterProduct.html', title='Products', form=form, all_prods=products, p=p, pagination=pagination, page=page,
                           per_page=per_page)

# displays all products with pagination on browse page-- has ability to filter all products
@bp.route('/products', methods=['GET', 'POST'])
def products():
    page, per_page, offset = get_page_args(page_parameter='page',
                                        per_page_parameter='per_page') # pagination variables

    products, total = Product.get_all(offset=offset, per_page=per_page)
    form = FilterForm()
    p = form.max_price.data # price
    c = form.category.data # category
    kw = form.keyword.data # keyword
    if form.validate_on_submit():
        # determine which filter should be applied and run appropriate query
        if p:
            products, total = Product.get_by_price(p, offset=offset, per_page=per_page)
        elif c:
            products, total = Product.get_by_category(c, offset=offset, per_page=per_page)
        else:
            products, total = Product.get_by_common_word(kw, offset=offset, per_page=per_page)

    pagination = Pagination(page=page, per_page=per_page, total=total, show_single_page=True)

    return render_template('filterProduct.html', title='Products', form=form, all_prods=products, p=p, pagination=pagination, page=page,
                           per_page=per_page)

# displays product details, product reviews, product sellers, and has functionality to add product to cart
@bp.route('/product_<product_id>', methods=['GET', 'POST'])
def product_details(product_id):
    product = Product.get(product_id) # product details
    reviews = Product_Review.get_by_pid(product_id) # reviews for given product
    sellers = Inventory.get_by_pid(product_id) # sellers for given product

    seller_ids = [] # list of seller ids
    sellers2 = [] # list of all seller information (including name)
    inv_ids = [] # list of inventory ids
    quantities = [] # list of quantities associated with each product,seller pair
    for s in sellers:
        seller_info = Inventory.get_seller_name(product_id, s.uid)
        sellers2.append(seller_info)
        seller_ids.append(s.uid)
        inv_ids.append(s.id)
        quantities.append(s.quantity)

    if request.method == "POST":
        sellerId = int(request.form.get("sellerId"))
        quantity = int(request.form.get("quant"))
        idx = seller_ids.index(sellerId)

        # quantity is a required field  
        if not quantity:
            return render_template('productDetails.html', title='ProductDetails', product=product, reviews=reviews, sellers=sellers2, failed = 3, current_user=current_user)

        # quantity cannot be more than a given seller has
        if quantity > int(quantities[idx]):
            return render_template('productDetails.html', title='ProductDetails', product=product, reviews=reviews, sellers=sellers2, failed = 1, current_user=current_user)
        else:
            # successfully added product to cart
            Cart.add_to_cart(current_user.id, sellerId, inv_ids[idx], product_id, quantity)
            return render_template('productDetails.html', title='ProductDetails', product=product, reviews=reviews, sellers=sellers2, failed = 2, current_user=current_user)
    
    return render_template('productDetails.html', title='ProductDetails', product=product, reviews=reviews, sellers=sellers2, failed = 0, current_user=current_user)
