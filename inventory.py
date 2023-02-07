from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, DecimalField, SelectField
from wtforms.validators import InputRequired, NumberRange
from wtforms import IntegerField, SubmitField, SelectField, StringField, DecimalField
from wtforms.validators import InputRequired, NumberRange, Optional, Length
from flask import Blueprint

from .models.product import Product
from .models.inventory import Inventory
from .models.user import User
from .models.order_content import Order_Content
from .models.inventory_analyze import Product_Rank

from flask import Blueprint

bp = Blueprint('inventory', __name__)

@bp.route('/seller/<uid>', methods=['GET'])
def seller(uid):
    curr_user = User.get(uid)
    if curr_user.isSeller == 0:
        print('bugger')
        return render_template("seller_register_page.html", uid=uid)
    else:
        return render_template("seller.html", uid=uid)

# form that allows a user to become a seller
class becomeSellerForm(FlaskForm):
    confirm = SelectField('Do you want to become a seller?', choices=["Yes", "No"])
    submit = SubmitField('Confirm')

# allows a user to become a seller 
@bp.route('/become-seller/<uid>', methods=['GET', 'POST'])
def becomeSeller(uid):
    form = becomeSellerForm()
    confirmation = form.confirm.data
    if form.validate_on_submit():
        if confirmation == "No":
            # if user does not want to become seller
            return redirect(url_for("inventory.seller", uid=uid))
        else:
            # if seller does want to become seller
            beSeller = User.become_seller(uid)
            if beSeller == False:
                # user is already a seller
                return redirect(url_for("inventory.becomeSeller", uid=uid, failed=1))
            else:
                # user successfully becomes seller
                return redirect(url_for("inventory.seller", uid=uid, failed=2))
    return render_template("become_seller.html", form=form, uid=uid, failed=0)
    
@bp.route('/inventory/', methods=['GET','POST'])
def inventory():
    if request.method == 'POST':
        if request.form['action'] == 'remove':
            Inventory.deactivate_inventory(request.form['uid'], request.form['pid'])
        if request.form['action'] == 'reactivate':
            Inventory.reactivate_inventory(request.form['uid'], request.form['pid'])
    active_seller_prods = Product.get_active_seller_prods(current_user.id)
    inactive_seller_prods = Product.get_inactive_seller_prods(current_user.id)

    return render_template("inventory.html", products = active_seller_prods, inactive_prods = inactive_seller_prods)

@bp.route('/inventory/purchase_history', methods=['GET','POST'])
def purchase_history():
    purchase = Order_Content.get_all_by_sid(current_user.id)
    user = User.get(current_user.id)
    return render_template("purchase_view.html", purchase = purchase, user = user)

@bp.route('/inventory/sellerOutput/<persid>')
def sellerOutput(persid):
    items = Inventory.get_by_uid(persid)
    if(len(items)<=0):
        items = []
    for item in items:
        print(item.pid)
    return render_template('sellerInventoryOutputWithSearch.html', name = persid, items = items)

# form for adding an entirely new product
class AddNewProductForm(FlaskForm):
    product_name = StringField('Enter product name', validators=[InputRequired()])
    product_category = StringField('Enter product category', validators=[InputRequired(), Length(max=50)])
    product_description = StringField('Enter product description', validators=[InputRequired(), Length(max=200)])
    product_price = DecimalField('Enter product price', validators=[InputRequired(), NumberRange(min=1)])
    quantity = IntegerField('Enter inventory quantity', validators=[InputRequired(), NumberRange(min=0, message="Quantity should >= 0")])
    submit = SubmitField('Confirm')

# adds new product to products table and updates inventory quantity
@bp.route('/add-new-product', methods=['GET', 'POST'])
def add_new_product():
    uid = current_user.id
    form = AddNewProductForm()
    if form.validate_on_submit():
        # product cannot be an existing product-- "same" product in our case means
        # same name 
        if Product.validate_product(form.product_name.data):
            new_pid = Product.add_new_product(form.product_name.data, form.product_category.data, form.product_description.data, form.product_price.data)
            # if our product was successfully added, we now have its product id to update the inventory table
            if new_pid:
                # successfully added new product
                Inventory.add_existing_product(new_pid, uid, form.quantity.data)
                return redirect(url_for('inventory.inventory', uid=uid))
        else:
            # product already exists-- failed to add product
            return render_template('addInventory.html', form=form, failed=1)
    return render_template('addInventory.html', form=form, failed=0)

# form for adding an existing product to inventory
class AddExistingProductForm(FlaskForm):
    pid = IntegerField('Product ID', validators=[Optional()])
    product_name = StringField('Product name', validators=[Optional()])
    quantity = IntegerField('Quantity',
                            validators=[InputRequired(), NumberRange(min=0, message="Quantity should >= 0")])
    submit = SubmitField('Confirm')

# adds an existing product to a seller's inventory-- inserts into inventory new pid,uid pair
@bp.route('/add-existing-Product', methods=['GET', 'POST'])
def add_existing_product():
    newly_added_pid = -1
    uid = current_user.id
    if request.method == 'GET':
        newly_added_pid = request.args.get('pid', -1)
    
    if request.method == 'POST':
        # quantity is a required field
        if not request.form.get('quant'):
            return render_template('addExistingProduct.html', title='Add Existing Product', uid=uid,
                           newly_added_pid=newly_added_pid, failed=3)
        # product id is a required field
        if request.form.get('pid'):
            new_product = Inventory.add_existing_product(request.form.get('pid'), uid, request.form.get('quant'))
            if new_product is False:
                # product already exists in inventory or does not exist in products table
                return render_template('addExistingProduct.html', title='Add Existing Product', uid=uid,
                           newly_added_pid=newly_added_pid, failed=1)
            else:
                # successfully added existing product
                return render_template('addExistingProduct.html', title='Add Existing Product', uid=uid,
                           newly_added_pid=newly_added_pid, failed=2)

    return render_template('addExistingProduct.html', title='Add Existing Product', uid=uid,
                           newly_added_pid=newly_added_pid, failed=0)


class EditFulfillmentForm(FlaskForm):
    status = SelectField('Fulfillment status', choices=["Fulfilled", "In Progress"])
    submit = SubmitField('Confirm')

@bp.route('/edit-fulfillment/<oid>/<inventory_id>', methods=['GET', 'POST'])
def editFulfillment(oid, inventory_id):
    order = Order_Content.get_all_by_order_id(oid)
    form = EditFulfillmentForm()
    if form.validate_on_submit():
        i = 0
        if(form.status.data=='Fulfilled'):
            Order_Content.change_fulfillment(oid, inventory_id, 'fulfilled')
        elif(form.status.data=='In Progress'):
            Order_Content.change_fulfillment(oid, inventory_id, 'in_progress')
        flash("Successfully changed")
        return redirect(url_for('inventory.purchase_history'))
    return render_template('editFulfillment.html', form=form, order=order, oid=oid, inventory_id=inventory_id)

# form for editing product details and inventory quantity
class EditInventoryForm(FlaskForm):
    product_name = StringField('Enter new product name', validators=[Optional()])
    product_category = StringField('Enter new product category', validators=[Optional(), Length(max=50)])
    product_description = StringField('Enter new product description', validators=[Optional(), Length(max=200)])
    product_price = DecimalField('Enter new product price', validators=[Optional(), NumberRange(min=1)])
    quantity = IntegerField('Enter new inventory quantity', validators=[Optional(), NumberRange(min=0, message="Quantity should >= 0")])
    submit = SubmitField('Confirm')
    
# allows for editing product information and its relevant inventory quantity
@bp.route('/edit-inventory/<pid>/<uid>', methods=['GET', 'POST'])
def editInventory(pid, uid):
    inventory = Inventory.get_inventory_id(uid, pid) # get all inventory information
    product_details = Product.get(pid) # get current product details
    
    # keep track of current values so that a user can select which attributes they want to change
    # without having to input values for every attribute
    name = product_details.name
    category = product_details.category
    description = product_details.description
    price = product_details.price
    quantity = inventory.quantity

    form = EditInventoryForm()
    if form.validate_on_submit():
        # check which attributes the user inputed and update values
        if form.quantity.data:
            quantity = form.quantity.data
        if form.product_name.data:
            name = form.product_name.data
        if form.product_category.data:
            category = form.product_category.data
        if form.product_description.data:
            description = form.product_description.data
        if form.product_price.data:
            price = form.product_price.data

        Inventory.change_quantity(pid, uid, quantity) # update inventory quantity
        Product.update_product(pid, name, category, description, price) # update product details
        flash("Successfully changed")
        return redirect(url_for('inventory.inventory', uid=uid))
    return render_template('editInventory.html', form=form, pid=pid, uid=uid)

@bp.route('/inventory/<uid>', methods=['GET'])
def inventoryAnalyze(uid):
    top_products = Product_Rank.top_ten_products(uid)
    worst_products= Product_Rank.worst_ten_products(uid)
    lowest_products = Product_Rank.lowest_ten_products(uid)
    return render_template("inventory_analyze.html", top_products=top_products, worst_products = worst_products, lowest_products = lowest_products, uid=uid)
