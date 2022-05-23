from itsdangerous import Serializer 
from market import db, login_manager
from market import bcrypt
from flask_login import UserMixin
from flask import Flask

app = Flask(__name__)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    items = db.relationship('Item', backref='owned_user', lazy=True)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_sell(self, item_obj):
        return item_obj in self.items

    def get_token(self):
        serial = Serializer('ec9439cfc6c796ae2029594d')
        return serial.dumps({'user_id' :self.id})

    @staticmethod
    def varify_token(token):
        serial = Serializer('ec9439cfc6c796ae2029594d')
       
        try:
            user_id = serial.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False)
    description = db.Column(db.String(length=1024), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    pickup_address = db.Column(db.String(length=1024), nullable=False)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'Item {self.name}'

    def buy(self, user):
        self.owner = user.id
        db.session.commit()

    def sell(self, user):
        self.owner = user.id
        db.session.commit()



class Request(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    item_id = db.Column(db.Integer(), db.ForeignKey('item.id'))
    item_name = db.Column(db.String(length=1024), nullable=False)
    buyer_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    seller_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    buyer_name = db.Column(db.String(length=1024), nullable=False)
    status= db.Column(db.Integer(),nullable=False)

class Auth(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    customer_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    auth_code = db.Column(db.String())
    

