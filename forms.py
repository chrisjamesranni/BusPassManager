from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from my_models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose another one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use another one.')

class StudentProfileForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired(), Length(max=20)])
    department = StringField('Department', validators=[DataRequired(), Length(max=100)])
    year = IntegerField('Year', validators=[DataRequired()])
    semester = IntegerField('Semester', validators=[DataRequired()])
    location_id = SelectField('Location', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Profile')

class CardRequestForm(FlaskForm):
    request_type = SelectField('Request Type', choices=[
        ('new', 'New Card'), 
        ('cancel', 'Cancel Card'), 
        ('replace', 'Replace Card')
    ], validators=[DataRequired()])
    reason = TextAreaField('Reason', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Submit Request')

class LocationForm(FlaskForm):
    name = StringField('Location Name', validators=[DataRequired(), Length(max=100)])
    address = StringField('Address', validators=[Optional(), Length(max=255)])
    distance = FloatField('Distance from College (km)', validators=[DataRequired()])
    fee_amount = FloatField('Fee Amount', validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Save Location')

class PaymentForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('upi', 'UPI')
    ], validators=[DataRequired()])
    description = StringField('Description', validators=[Optional(), Length(max=255)])
    academic_year = StringField('Academic Year', validators=[DataRequired(), Length(max=20)])
    semester = StringField('Semester', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Make Payment')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    role = SelectField('Role', choices=[
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('accountant', 'Accountant'),
        ('student', 'Student')
    ], validators=[DataRequired()])
    is_active = BooleanField('Active')
    password = PasswordField('Password', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    submit = SubmitField('Save User')

class QRScanForm(FlaskForm):
    student_id = HiddenField('Student ID')
    submit = SubmitField('Check Status')

class UpdateCardStatusForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    card_status = SelectField('Card Status', choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired')
    ], validators=[DataRequired()])
    fee_status = SelectField('Fee Status', choices=[
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue')
    ], validators=[DataRequired()])
    current_dues = FloatField('Current Dues', validators=[Optional()])
    fine_amount = FloatField('Fine Amount', validators=[Optional()])
    submit = SubmitField('Update Status')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class NotificationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    message = TextAreaField('Message', validators=[DataRequired()])
    notification_type = SelectField('Type', choices=[
        ('payment', 'Payment'),
        ('card', 'Card'),
        ('general', 'General')
    ], validators=[DataRequired()])
    user_id = SelectField('User', coerce=int, validators=[Optional()])
    all_users = BooleanField('Send to all users')
    submit = SubmitField('Send Notification')
