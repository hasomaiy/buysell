from traceback import print_exc
from unicodedata import name
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError,NumberRange
from market.models import User


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address')

    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')


class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label='Purchase Item!')

class SellItemForm(FlaskForm):
    submit = SubmitField(label='Sell Item!')

class SellerItemForm(FlaskForm):
    name = StringField(label='Item Name:', validators=[Length(min=2, max=30), DataRequired()])
    price = StringField(label='Item Price:', validators=[Length(min=2, max=30), DataRequired()])
    description = StringField(label='Item Description:', validators=[Length(min=2, max=150), DataRequired()])
    pickup_address = StringField(label='Pick Up Address:', validators=[Length(min=2, max=150), DataRequired()])
    submit = SubmitField(label='Sell Item!')

class RequestForm(FlaskForm):
    submit = SubmitField(label='OK')

class ResetRequestForm(FlaskForm):
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    submit = SubmitField(label='Reset Password', validators=[DataRequired()])

class ChangePasswordForm(FlaskForm):
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Change Password', validators=[DataRequired()])

class LoginAuthCodeForm(FlaskForm):
    auth_code = StringField(label='Google Authentication Code:')
    submit = SubmitField(label='Verify')

class ForgetUserNameForm(FlaskForm):
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    submit = SubmitField(label='Send email')