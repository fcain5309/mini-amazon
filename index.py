from flask import render_template, redirect, url_for
from flask_login import current_user
import datetime
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired

from .models.product import Product
from .models.order_content import Order_Content

from flask import Blueprint
bp = Blueprint('index', __name__)

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Go')

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    products = Product.get_all()
    if form.validate_on_submit():
        products = Product.get_by_common_word(form.search.data)
        return redirect(url_for('products.search', search = form.search.data))
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Order_Content.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))

        if (purchases is None):
            purchases = []
    else:
        purchases = None
    # render the page by adding information to the index.html file
    return render_template('index.html',
                           title='Products', 
                           form=form,
                           avail_products=products,
                           purchase_history=purchases)

