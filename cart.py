from wsgiref import validate
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import ValidationError, DataRequired, NumberRange
import decimal


from .models.cart import Cart
from .models.user import User


from flask import Blueprint
bp = Blueprint('cart', __name__)

class FilterForm(FlaskForm):
    id_list = IntegerField('New Quantity:', validators=[NumberRange(min=0, message = "min ID 0")])
    submit = SubmitField('Update')
    def validate_id(self, id_list):
        if not isinstance(id_list, int):
            raise ValidationError('Input must be an integer')

# develops the home page for cart. displays cart contents, and buttons for updating them or submitting an order
@bp.route('/cart', methods=['GET', 'POST'])
def get_prod_per_user():
    final_total = 0    
    print(current_user)
    print(current_user.is_authenticated)
    if current_user.is_authenticated == True:
        print(current_user)
        user_cart = Cart.get_items_for_user(current_user.id)
        for row in range(len(user_cart)):
            if user_cart[row][7] == 'in_cart':
                price = user_cart[row][2]
                final_total += price   
    else:
        user_cart = None
        current_user.id = None 
    return render_template('cart.html',
                           cart_prod_list=user_cart,
                           buy_uid = current_user.id,
                           final_total = final_total
                           )

# takes user to a page where they can select an item from their cart to change quantity for
@bp.route('/cart/update', methods=['GET', 'POST'])
def update_quant():
    has_submitted = False
    product_list = Cart.only_prods(current_user.id)
    form = FilterForm()
    has_updated = False
    
    if request.method == 'POST':

        has_submitted = True
        ret_form = request.form['product']
        string = ret_form.replace("(", "") 
        x = string.split(",")
        pid = x[0]
        print(pid)
        
        return redirect(url_for('cart.update_quant_step2',pid = pid
                        ))  
                  
    else:   
        
        return render_template('cart_update.html',
                           product_list = product_list,
                           buy_uid = current_user.id,
                           form = form,
                           has_submitted=has_submitted,
                           pid = ""
                           )                        

# allows user to change the quantity of any specific product in their cart
@bp.route('/cart/update/<pid>', methods=['GET', 'POST'])
def update_quant_step2(pid):
    has_submitted = True
    product_list = Cart.only_prods(current_user.id)
    form = FilterForm()
    has_updated = False
    
    if request.method == 'POST':
        print("We are inside the post yay!")
        has_updated = True
        
        quantity = int(request.form["quantity"])
        to_update = Cart.update_cart_quant(current_user.id, quantity, pid) 
        return redirect(url_for('cart.get_prod_per_user'))  
                  
    else:   
        
        return render_template('cart_update_step2.html',
                           product_list = product_list,
                           buy_uid = current_user.id,
                           form = form,
                           has_submitted=has_submitted,
                           pid = pid
                           )                           

# allows user to submit all "in_cart" items to place an order
@bp.route('/cart/submit', methods=['GET', 'POST'])
def submit_order():   
    user_order = Cart.order_submission()
    final_total = 0 
    for row in range(len(user_order)):
        if type(user_order[row][1]) is decimal.Decimal:
            price = user_order[row][1]
            final_total += price   
    return render_template('order_submit.html',
                            order_list=user_order,
                            final_total= final_total)

# removes a line item from the user cart when they press the "remove" button
@bp.route('/cart/<pid>/<sell_uid>', methods=['GET', 'POST'])
def del_item(pid, sell_uid):
    
    
    user_update = Cart.delete_item_from_cart(current_user.id, pid, sell_uid)
    user_cart = Cart.get_items_for_user(current_user.id)
    num_prods = list(range(0, len(user_cart)))
    return render_template('cart.html',
                            cart_prod_list=user_cart,
                            buy_uid=current_user.id,
                            )
# clicking the status button on any line item on their cart allows a user to switch it back and forth
# from in_cart to save_for_later
@bp.route('/cart/upd/<pid>/<sell_uid>', methods=['GET', 'POST'])
def make_in_cart(pid, sell_uid):
    final_total = 0    
    user_change = Cart.move_to_cart(current_user.id, pid, sell_uid)
    user_cart = Cart.get_items_for_user(current_user.id)
    for row in range(len(user_cart)):
        if user_cart[row][7] == 'in_cart':
            price = user_cart[row][2]
            final_total += price   
    return render_template('cart.html',
                            cart_prod_list=user_cart,
                            buy_uid=current_user.id,
                            final_total=final_total
                            ) 
# function to display all the detailed order contents for past purchase
@bp.route('/user_account_history/<oid>', methods=['GET', 'POST'])
def detailed_order(oid):
    order_contents = Cart.order_content_page(oid)
    order_buyer = Cart.get_order_buyer(oid)[0][0]
    buyer_name = User.get_name(order_buyer)
    if current_user.is_authenticated:
        current_uid = current_user.id
    else:
        current_uid = None
    return render_template('detailed_order_page.html',
                            order_buyer=order_buyer, buyer_name = buyer_name,
                            current_uid = current_uid,
                            order_contents=order_contents
                            )