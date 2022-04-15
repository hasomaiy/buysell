
from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User,Request,Transaction
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm,RequestForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/',methods=['GET', 'POST'])
@app.route('/home',methods=['GET', 'POST'])
def home_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        print(attempted_user,form.password.data,'DD')
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    # return render_template('login.html', form=form)

    return render_template('home.html',form=form)

@app.route('/buy', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    if request.method == "POST":
        #Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for {p_item_object.price}$", category='success')
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item_object.name}!", category='danger')
        
        return redirect(url_for('market_page'))

    if request.method == "GET":
        items = Item.query.filter(Item.owner!=current_user.id)
        # items = Item.query.all()
        # owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/profile',methods=['GET', 'POST'])
def profile_page():
    # if request.method == "GET":

    bought_items = Transaction.query.filter(Transaction.buyer_id==current_user.id)
    sold_items = Transaction.query.filter(Transaction.seller_id==current_user.id)
    # items = Item.query.all()
    # owned_items = Item.query.filter_by(owner=current_user.id)
    return render_template('profile.html', bought_items=bought_items,sold_items=sold_items)


@app.route('/sell',methods=['GET', 'POST'])
def sell_page():
    
    selling_form = SellItemForm()
    
    if request.method == "POST":
        #Sell Item Logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"Congratulations! You sold {s_item_object.name} back to market!", category='success')
            else:
                flash(f"Something went wrong with selling {s_item_object.name}", category='danger')


        return redirect(url_for('sell_page'))

    if request.method == "GET":
        # items = Item.query.filter_by(owner=None)
        # items = Item.query.all()
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('sell.html', owned_items=owned_items, selling_form=selling_form)


@app.route('/requests',methods=['GET', 'POST'])
def requests_page():
    request_form = RequestForm()
    if request.method == "POST":
        #Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for {p_item_object.price}$", category='success')
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item_object.name}!", category='danger')
        
        return redirect(url_for('market_page'))

    if request.method == "GET":
        requests = Request.query.filter(Request.seller_id ==current_user.id,Request.status =="0")
        # items = Item.query.all()
        # owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('request.html', requests=requests, request_form=request_form)








