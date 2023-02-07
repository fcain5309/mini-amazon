from flask import render_template, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, BooleanField, SubmitField, SelectField, DecimalField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, InputRequired, NumberRange, Optional
import datetime

from .models.user import User
from .models.specific_order import Specific_Order


from flask import Blueprint
bp = Blueprint('users', __name__)

# standard provided login FlaskForm
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# allows users to login 
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    success = True
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            success = False
            return render_template('login.html', title='Sign In', form=form, success=success)
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, success=success)

# registration FlaskForm, now includes address as well
class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

# allows new users to register
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    success=False
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data, form.address.data):
            success=True
    return render_template('register.html', title='Register', form=form, success=success)

# allows users to logout
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

# sets up a page which displays basic account summary info
@bp.route('/account_summary', methods=['GET', 'POST'])
def account_summary():
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))
    uid = current_user.id
    email = current_user.email
    firstname = current_user.firstname
    lastname = current_user.lastname
    amount = current_user.amount
    address = current_user.address
    isSeller = current_user.isSeller

    return render_template('account_summary.html',
                            uid = uid, email = email, firstname = firstname,
                            lastname = lastname, amount = amount, address = address,
                            is_seller = isSeller)

# FlaskForm to search for users by name, email, or user id
# multiple submit forms buttons are used because the form also includes a HTML/JS question to choose what to display
# and that information is difficult to convey back to Flask without creating separate submit buttons
class uid_search_form(FlaskForm):
    uid_input = IntegerField('User ID', validators=[Optional()])
    name_input = StringField('Name', validators=[Optional()])
    email_input = StringField('Email', validators=[Optional(), Email()])
    submit_uid = SubmitField('Search User')
    submit_name = SubmitField('Search User')
    submit_email = SubmitField('Search User')

# sets up system to search up users
@bp.route('/search_user', methods=['GET', 'POST'])
def search_user():
    form = uid_search_form()
    if form.submit_uid.data:
        uid = form.uid_input.data
        user_data = User.get_all_uid_data(uid)
    elif form.submit_name.data:
        name = form.name_input.data
        user_data = User.get_data_by_name(name)
    elif form.submit_email.data:
        email = form.email_input.data
        user_data = User.get_data_by_email(email)
    else:
        user_data = "not_submitted"
    return render_template('user_view.html',
                                form = form,
                                user_data=user_data)

# renders the user public view
@bp.route('/user_<uid>', methods=['GET', 'POST'])
def user_public_page(uid):
    currentuserid = "-1"
    if current_user.is_authenticated:
        currentuserid = current_user.id
    user_data = User.get_all_uid_data(uid)
    return render_template('user_view_indiv.html',
                            user_data=user_data, persid = currentuserid)

# FlaskForm to update account information
class update_account_form(FlaskForm):
    firstname = StringField('First Name', default="")
    lastname = StringField('Last Name', default="")
    address = StringField('Address', default="")
    password = StringField('Password', default="")
    email = StringField('Email', default="")
    submit = SubmitField('Submit')

# allows users to update their account information, and also makes sure information is valid
# ex: ensures email is unique
@bp.route('/update_account', methods=['GET', 'POST'])
def update_account():
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))
    uid = current_user.id
    form = update_account_form()
    
    updated_fields = []
    if form.validate_on_submit():
        if form.firstname.data != "":
            error = User.update_firstname(uid, form.firstname.data)
            if error != "":
                form.firstname.errors.append(error)
            else:
                updated_fields.append("first name")
        if form.lastname.data != "":
            error = User.update_lastname(uid, form.lastname.data)
            if error != "":
                form.lastname.errors.append(error)
            else:
                updated_fields.append("last name")
        if form.address.data != "":
            error = User.update_address(uid, form.address.data)
            if error != "":
                form.address.errors.append(error)
            else:
                updated_fields.append("address")
        if form.password.data != "":
            error = User.update_password(uid, form.password.data)
            if error != "":
                form.password.errors.append(error)
            else:
                updated_fields.append("password")
        if form.email.data != "":
            error = User.update_email(uid, form.email.data)
            if error != "":
                # checks if there is a duplicate email in the database
                if 'duplicate key value violates unique constraint "users_email_key"' in error:
                    error = "There already is an account attached to this email"
                form.email.errors.append(error)
            else:
                updated_fields.append("email")
    
    # sets up message to notify user of successful information updates
    if len(updated_fields) == 0:
        message = None
    elif len(updated_fields) == 1:
        message = "Successfully updated " + updated_fields[0] + "."
    else:
        if len(updated_fields) > 2:
            for i in range(len(updated_fields) - 1, 0, -1):
                updated_fields.insert(i, ", ")
        else:
            updated_fields.insert(-1, " ")
        updated_fields.insert(-1, "and ")
        message = "Successfully updated " + ''.join(updated_fields) + "."

    return render_template('account_settings.html',
                            form = form, current_user = current_user, message=message)

# FlaskForm to apllow for deposits/withdrawals
class depo_with_form(FlaskForm):
    depo_or_with = SelectField(choices=['Deposit', 'Withdrawal'], validate_choice=True)
    depo_with_amount = DecimalField('Amount', places=2, validators=[InputRequired(), NumberRange(min=0.005, message="Input must be a positive number")])
    submit = SubmitField('Submit')

    # custom validation function
    def validate(self):
        if not FlaskForm.validate(self):
            return False
        else:
            # checks if the user is trying to withdraw more money than is available in the account
            if self.depo_or_with.data == "Withdrawal" and self.depo_with_amount.data > User.get_user_balance(current_user.id)[0][0]:
                self.depo_with_amount.errors.append('Cannot withdraw larger amount than account balance')
                return False
        return True

# allows user to deposit and withdraw funds
@bp.route('/depo_with', methods=['GET', 'POST'])
def depo_with():
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = depo_with_form()
    if form.validate_on_submit():
        submitted = True
        uid = current_user.id
        amount = form.depo_with_amount.data
        if form.depo_or_with.data == "Deposit":
            mult = 1
        else:
            mult = -1
        amount = mult * amount
        time_stamp = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
        User.depo_with(uid, amount, time_stamp)
    else:
        submitted = False
        time_stamp = None
        amount = 0
    # the form should require 2 decimal places, but this is here just to make sure
    amount = abs(round(amount, 2))

    return render_template('depo_with.html',
                        submitted = submitted, amount = amount, time_stamp = time_stamp, form = form, uid = current_user.id)

# FlaskForm to choose which types of transactions (deposits/withdrawals, order purchases, sold products) to display
class account_history_checkboxes(FlaskForm):
    depo_with = BooleanField('Deposits and withdrawals', default='checked')
    orders = BooleanField('Purchased Orders', default='checked')
    sold = BooleanField('Sold Products', default='checked')
    submit = SubmitField('Filter')

# display account transaction history
@bp.route('/account_history', methods=['GET', 'POST'])
def account_history():
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = account_history_checkboxes()
    depo_with = form.depo_with.data
    orders = form.orders.data
    sold = form.sold.data
    uid = current_user.id
    account_balance = current_user.amount
    # these queries are honestly terrible but it works I guess so why change it
    if depo_with and orders and not sold:
        history = User.get_user_combined_acct_hist(uid)
    elif depo_with and not orders and not sold:
        history = User.get_user_depo_with_acct_hist(uid)
    elif not depo_with and orders and not sold:
        history = User.get_user_orders_acct_hist(uid)
    elif (depo_with or orders) and sold:
        if depo_with and not orders:
            subset = "depo_with_acct_hist"
        elif orders and not depo_with:
            subset = "order_acct_hist"
        else:
            subset = "combined_acct_hist"
        history = User.get_user_sold_acct_hist(uid, subset)
    elif not depo_with and not orders and sold:
        history = User.get_sell_acct_hist(uid)
    else:
        history = None
 
    return render_template('account_history.html',
                            amount = account_balance,
                            form = form,
                           history=history)

# FlaskForm for purchase history
# multiple submit forms buttons are used because the form also includes a HTML/JS question to choose what to display
# and that information is difficult to convey back to Flask without creating separate submit buttons
class purchase_history_form(FlaskForm):
    order_sort_by_column = SelectField('Order Sort By', choices=['Time', 'Order ID', 'Total Cost', 'Number of (Unique) Items', 'Number of (Total) Items', 'Status'], validators=[Optional()], render_kw={'onchange': "myFunction()"})
    order_sort_by_order = SelectField('Order Order', choices=['Descending', 'Ascending'], validators=[Optional()], render_kw={'onchange': "myFunction()"})
    item_sort_by_column = SelectField('Item Sort By', choices=['Product Name', 'Category', 'Order ID', 'Time', 'Seller Last Name', 'Quantity', 'Price Per Item', 'Total Price', 'Status'], validators=[Optional()], render_kw={'onchange': "myFunction()"})
    item_sort_by_order = SelectField('Item Order', choices=['Descending', 'Ascending'], validators=[Optional()], render_kw={'onchange': "myFunction()"})
    search_bar = StringField('Search Value', validators=[Optional()])
    submit_order = SubmitField('View Purchase History')
    submit_item = SubmitField('View Purchase History')

# reveal a user's purchase history - allows for searching either on a order by order basis, or on a line item by line item basis
# for the line item view, a search bar is also provided which can search product name, catgory, and seller first and/or last name
@bp.route('/purchase_history', methods=['GET', 'POST'])
def purchase_history():
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))
    # these dictionaries map data from the form to the corresponding column names in the SQL database
    order_column_map = {'Time': 'time_stamp', 'Order ID': 'id', 'Total Cost': 'total_price', 'Number of (Unique) Items': 'unique_items', 'Number of (Total) Items': 'total_items', 'Status': 'status'}
    item_column_map = {'Product Name': "product_name", "Product ID": "product_id", "Seller Last Name": "seller_lastname", "Seller ID": "seller_uid", "Order ID": "order_id",
        "Time": "time_stamp", "Category": "category", "Price Per Item": "price", "Total Price": "total_price", "Quantity": "quantity", "Status": "item_status"}
    asc_desc_map = {'Ascending': 'ASC', 'Descending': "DESC"}
    form = purchase_history_form()
    order_column_raw = form.order_sort_by_column.data
    order_order_raw = form.order_sort_by_order.data
    item_column_raw = form.item_sort_by_column.data
    item_order_raw = form.item_sort_by_order.data
    if form.submit_order.data:
        data_type = "Order"
        data = Specific_Order.sort_orders_by(current_user.id, order_column_map[order_column_raw], asc_desc_map[order_order_raw])
    elif form.submit_item.data:
        data_type = "Line Item"
        # sim_str is a string that is used to search - any line item with product name, catgory, or seller first and/or last name containing sim_str will be returned
        sim_str = ''
        if form.search_bar.data:
            sim_str = form.search_bar.data
        data = Specific_Order.sort_items_by(current_user.id, item_column_map[item_column_raw], asc_desc_map[item_order_raw], sim_str)
    else:
        data_type = None
        data = "Failed"
 
    return render_template('purchase_history.html',
                            form=form,
                            data_type=data_type,
                            data=data)
