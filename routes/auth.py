from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from extension import db
from my_models import User, StudentProfile
from forms import LoginForm, RegistrationForm, ChangePasswordForm
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'staff':
            return redirect(url_for('staff.scan'))
        elif current_user.role == 'accountant':
            return redirect(url_for('accountant.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            if next_page:
                return redirect(next_page)
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'staff':
                return redirect(url_for('staff.scan'))
            elif user.role == 'accountant':
                return redirect(url_for('accountant.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    
    return render_template('login.html', form=form, title='Login', now=datetime.now())

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            role='student'
        )
        db.session.add(user)
        db.session.commit()
        
        # Create empty student profile
        student_profile = StudentProfile(
            user_id=user.id,
            student_id=f"STU{user.id:06d}",
            card_status='inactive'
        )
        db.session.add(student_profile)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('login.html', form=form, title='Register', register=True, now=datetime.now())

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.current_password.data):
            current_user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('auth.logout'))
        else:
            flash('Current password is incorrect!', 'danger')
    
    return render_template('login.html', form=form, title='Change Password', change_password=True, now=datetime.now())
