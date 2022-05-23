from io import BytesIO
from re import T
from tkinter import N
from turtle import title
from urllib import response

from sqlalchemy import true
from market import app,mail
from flask import render_template, redirect, send_file, session, url_for, flash, request
from market.models import Item, User,Request,Auth
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm,RequestForm,ResetRequestForm,ChangePasswordForm,SellerItemForm,LoginAuthCodeForm,ForgetUserNameForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from market import bcrypt
import qrcode
import pyotp
import json

@app.route('/',methods=['GET', 'POST'])
@app.route('/home',methods=['GET', 'POST'])
def home_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            # flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            # return redirect(url_for('market_page'))
            session["message"] = json.dumps(attempted_user.id)
            flash('Please enter Authentication Code to enjoy Buy And Sell Marketplace!', category='success')

            return redirect(url_for('qr_logincode'))
        else:
            flash('Username and password are not match! Please try again', category='danger')
    
    return render_template('home.html',form=form)

@app.route('/buy', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    if request.method == "POST":
        #Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        
        p_item_object = Item.query.filter_by(id=purchased_item).first()

        existing_req = Request.query.filter(Request.item_id==purchased_item,Request.buyer_id==current_user.id).first()

        if not existing_req:
            item_name = Item.query.filter(Item.id==purchased_item).first().name
            req_to_create = Request(item_id=purchased_item,item_name=item_name,buyer_id=current_user.id,\
                                    buyer_name=current_user.username,seller_id=p_item_object.owner,status=0)
            db.session.add(req_to_create)
            db.session.commit()
            user_Details = User.query.filter_by(id=p_item_object.owner).first()
            send_email_buy_request(user_Details,current_user,p_item_object)
            flash(f"You purchase request of {p_item_object.name} for {p_item_object.price}$ is sent\
                is sent to the Seller. You will see the item in your Profile once approved." , category='success')
        else:
            flash(f"Request for {p_item_object.name} already exists.\
                You will see the item in your Profile once approved." , category='success')

        return redirect(url_for('market_page'))

    if request.method == "GET":
        # sold_items = Request.query.filter(Request.status==1).all()
        sold_items= db.session.query(Request.item_id).filter(Request.status==1).all()
        ll=[]
        for i in sold_items:
             ll.append(i[0])

        items = Item.query.filter(Item.id.not_in(ll),Item.owner!=current_user.id)    
        
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
        # flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        session['userid'] = json.dumps(user_to_create.id)

        
        return redirect(url_for('qr_registrationcode'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/profile',methods=['GET', 'POST'])
def profile_page():
    
    bought_items = db.session.query(Request,Item).filter(Request.item_id==Item.id,Request.status==1,\
                    Request.buyer_id==current_user.id)
    
    sold_items = db.session.query(Request,Item).filter(Request.item_id==Item.id,Request.status==1,\
                    Request.seller_id==current_user.id)

                    
    return render_template('profile.html', bought_items=bought_items,sold_items=sold_items)


@app.route('/sell',methods=['GET', 'POST'])
def sell_page():
    selling_form = SellItemForm()
    if request.method == "GET":
        sold_items= db.session.query(Request.item_id).filter(Request.status==1).all()
        ll=[]
        for i in sold_items:
             ll.append(i[0])

        owned_items = Item.query.filter(Item.id.not_in(ll),Item.owner==current_user.id)
        return render_template('sell.html', owned_items=owned_items, selling_form=selling_form)

@app.route('/sell_items', methods=['GET', 'POST'])
def sell_items():
    form = SellerItemForm()

    
    if form.validate_on_submit():
        item_to_create =  Item(name=form.name.data,price=form.price.data,
                        description=form.description.data,pickup_address=form.pickup_address.data,owner= current_user.id)
        db.session.add(item_to_create)
        db.session.commit()

        flash(f'Success! Your item is now in marketplace: {form.name.data}', category='success')
        return redirect(url_for('sell_page'))


    return render_template('sell_items.html', form=form)



@app.route('/requests',methods=['GET', 'POST'])
def requests_page():
    request_form = RequestForm()
    if request.method == "POST":
        #Purchase Item Logic
        request_id = request.form.get('req_id')
        req_object = Request.query.filter(Request.id==request_id).first()
        if req_object:
            Request.query.filter(Request.item_id==req_object.item_id).\
            update({'status': 2})
            Request.query.filter(Request.id==request_id).\
            update({'status': 1})    
            db.session.commit()

            flash(f"You Approved {req_object.item_id} for {req_object.buyer_id}", category='success')
            
        return redirect(url_for('requests_page'))

    if request.method == "GET":
        requests = Request.query.filter(Request.seller_id ==current_user.id,Request.status ==0)
        # items = Item.query.all()
        # owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('request.html', requests=requests, request_form=request_form)

def send_email(user):
    
    token = User.get_token(user)
    msg = Message('Password Reset Request', recipients=[user.email_address],sender='streetanderson683@gmail.com')
    msg.body =f'''
    To Reset Password follow the link.
    
     {url_for('reset_token',token=token,_external=True)}
   

    If you did not send a reset password request, please ignore this message.




    '''

    mail.send(msg)

# Email on the basis of the request to puchase item
def send_email_buy_request(user,buyer,p_item_object):
    
    msg = Message(f'Buy Request on item{p_item_object.name}', recipients=[user.email_address],sender='streetanderson683@gmail.com')
    msg.body =f'''Hi {user.username},
    
    
    {buyer.username} has requested to buy item {p_item_object.name} with price {p_item_object.price}$.
   
    
    If you interested to sell {p_item_object.name} to {buyer.username}, please email back to {buyer.username}.

    {buyer.username}'s email-id is {buyer.email_address}.

    From,
    Buy And Sell


    '''

    mail.send(msg)


@app.route('/reset_password',methods=['GET', 'POST'])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user:
            send_email(user)
            flash('Reset request sent. Please check your email','success')
            # return render_template('reset_request.html', title = 'Reset Request',form = form)
            return redirect(url_for('home_page'))
        else:
            flash('user not there','failed')

    return render_template('reset_request.html',title='Reset Request',form= form)

@app.route('/reset_password/<token>',methods=['GET', 'POST'])
def reset_token(token):
    user = User.varify_token(token)
    if user is None:
        flash('That token is invalid. Please Try again!','warning')
        return redirect(url_for('reset_request'))

    form=ChangePasswordForm()
    if form.validate_on_submit():
        # user.password= bcrypt.generate_password_hash(form.password1.data).decode('utf-8')
        user.password =  form.password1.data
        db.session.commit()
        flash('Password Changed! Please Login.')
        return redirect(url_for('home_page'))
    return render_template('change_password.html',form = form)


def authgen(user,flag):
    if(flag == 0):
        auth = Auth.query.filter_by(customer_id = current_user.id).first()
        if(auth == None):
            key = pyotp.random_base32()     
            auth_to_create = Auth( customer_id=current_user.id,
                                auth_code=key)
            db.session.add(auth_to_create)
            db.session.commit()
        else:    
            key = auth.auth_code    

    elif(flag == 1):
        auth = Auth.query.filter_by(customer_id = current_user.id).first()   
        key = auth.auth_code
    
    print(key)        
    t = pyotp.TOTP(key) #secret key
    return t

@app.route('/qr_generation')
def qr_generation():
    # install pyotp and qurcode and Pillow library
    user = User.query.filter_by(id = current_user.id).first()
    t = authgen(user,1)
    auth_str = t.provisioning_uri(name= 'Buy Anad Sell',issuer_name='Buy And Sell')

    buffer = BytesIO()
    img = qrcode.make(auth_str)
    img.save(buffer)
    buffer.seek(0)
    response = send_file(buffer,mimetype='image/png')
    return response

@app.route('/qr_generationpage')
def qr_generationpage():
   return render_template('google_auth.html')

@app.route('/qr_logincode',methods=['GET', 'POST'])
def qr_logincode():
# install pyotp and qurcode and Pillow library
    authForm = LoginAuthCodeForm()
    if authForm.validate_on_submit():
        auth_code = request.form.get('auth_code')
        attempted_user_id = json.loads(session["message"])
        user = User.query.filter_by(id = attempted_user_id).first()
        login_user(user)
        t = authgen(user,1)
        if auth_code == t.now():
                login_user(user)
                flash(f'Success! You are logged in as: {user.username}', category='success')
                return redirect(url_for('market_page'))
        else:
                flash(f'Your Code mismatch! Please enter valid authentication code!', category='danger')


    return render_template('login_authcode.html', form=authForm)
        
@app.route('/qr_registrationcode',methods=['GET', 'POST'])
def qr_registrationcode():
# install pyotp and qurcode and Pillow library
    authForm = LoginAuthCodeForm()
    print("hello1")
    # if authForm.validate_on_submit():
    print("hello")
    auth_code = request.form.get('auth_code')
    attempted_user_id = json.loads(session['userid'])
    user = User.query.filter_by(id = attempted_user_id).first()
    t = authgen(user,0)
    print("hello")
    print(t.now())
    if auth_code == t.now():
    
        flash(f"Account created successfully! You are now logged in as {user.username}", category='success')
        return redirect(url_for('market_page'))
    else:
        flash(f'Your Code mismatch! Please enter valid authentication code!', category='danger')


    return render_template('google_auth_register.html', form=authForm)

@app.route('/qr_generation_registration')
def qr_generation_registration():
# install pyotp and qurcode and Pillow library
    user = User.query.filter_by(id = current_user.id).first()
    t = authgen(user,0)
    auth_str = t.provisioning_uri(name= 'Buy Anad Sell',issuer_name='Buy And Sell')

    buffer = BytesIO()
    img = qrcode.make(auth_str)
    img.save(buffer)
    buffer.seek(0)
    response = send_file(buffer,mimetype='image/png')
    return response
    
# Email on the basis of the request to puchase item
def send_email_forget_username(user):
    
    msg = Message(f'User name reset request', recipients=[user.email_address],sender='streetanderson683@gmail.com')
    msg.body =f'''Hi,
    
    You have got an user name rest request.
    
    Your User Name is : {user.username}


    From,
    Buy And Sell


    '''

    mail.send(msg)


@app.route('/reset_username',methods=['GET', 'POST'])
def reset_username():
    form = ForgetUserNameForm()
    if form.validate_on_submit():
        
        user = User.query.filter_by(email_address=form.email_address.data).first()
        print(user.email_address)
        if user:
            # print(user)
            send_email_forget_username(user)
            flash('Reset request sent. Please check your email','success')
            return redirect(url_for('home_page'))

        else:
            flash('user not there','failed')

    return render_template('forget_username.html',title='Reset Request',form= form)
