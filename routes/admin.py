from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from models import User, Location, StudentProfile, CardRequest, Notification, Payment
from forms import UserForm, LocationForm, NotificationForm, UpdateCardStatusForm
from sqlalchemy import func
import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to check if user is admin"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page!', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get counts for dashboard stats
    total_students = User.query.filter_by(role='student').count()
    active_cards = StudentProfile.query.filter_by(card_status='active').count()
    pending_requests = CardRequest.query.filter_by(status='pending').count()
    total_fees_collected = db.session.query(func.sum(Payment.amount)).filter(
        Payment.payment_status=='paid'
    ).scalar() or 0
    
    # Get recent card requests
    recent_requests = CardRequest.query.order_by(CardRequest.request_date.desc()).limit(5).all()
    
    # Get payment stats
    current_month = datetime.datetime.utcnow().month
    current_year = datetime.datetime.utcnow().year
    monthly_payments = db.session.query(func.sum(Payment.amount)).filter(
        func.extract('month', Payment.payment_date) == current_month,
        func.extract('year', Payment.payment_date) == current_year,
        Payment.payment_status == 'paid'
    ).scalar() or 0
    
    payment_data = db.session.query(
        func.extract('month', Payment.payment_date).label('month'),
        func.sum(Payment.amount).label('total')
    ).filter(
        func.extract('year', Payment.payment_date) == current_year,
        Payment.payment_status == 'paid'
    ).group_by('month').all()
    
    payment_months = [0] * 12
    for month, total in payment_data:
        payment_months[int(month)-1] = float(total)
    
    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        active_cards=active_cards,
        pending_requests=pending_requests,
        total_fees_collected=total_fees_collected,
        monthly_payments=monthly_payments,
        payment_months=payment_months,
        recent_requests=recent_requests
    )

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    form = UserForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            role=form.role.data,
            is_active=form.is_active.data
        )
        db.session.add(user)
        db.session.commit()
        
        if form.role.data == 'student':
            # Create empty student profile
            student_profile = StudentProfile(
                user_id=user.id,
                student_id=f"STU{user.id:06d}",
                card_status='inactive'
            )
            db.session.add(student_profile)
            db.session.commit()
        
        flash('User created successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/manage_users.html', form=form, title='New User')

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone = form.phone.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/manage_users.html', form=form, title='Edit User', user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete yourself!', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/locations')
@login_required
@admin_required
def locations():
    locations = Location.query.all()
    return render_template('admin/manage_locations.html', locations=locations)

@admin_bp.route('/locations/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_location():
    form = LocationForm()
    if form.validate_on_submit():
        location = Location(
            name=form.name.data,
            address=form.address.data,
            distance=form.distance.data,
            fee_amount=form.fee_amount.data,
            is_active=form.is_active.data
        )
        db.session.add(location)
        db.session.commit()
        flash('Location added successfully!', 'success')
        return redirect(url_for('admin.locations'))
    
    return render_template('admin/manage_locations.html', form=form, title='New Location')

@admin_bp.route('/locations/edit/<int:location_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    form = LocationForm(obj=location)
    
    if form.validate_on_submit():
        location.name = form.name.data
        location.address = form.address.data
        location.distance = form.distance.data
        location.fee_amount = form.fee_amount.data
        location.is_active = form.is_active.data
        db.session.commit()
        flash('Location updated successfully!', 'success')
        return redirect(url_for('admin.locations'))
    
    return render_template('admin/manage_locations.html', form=form, title='Edit Location', location=location)

@admin_bp.route('/locations/delete/<int:location_id>', methods=['POST'])
@login_required
@admin_required
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    
    # Check if students are assigned to this location
    students = StudentProfile.query.filter_by(location_id=location_id).first()
    if students:
        flash('Cannot delete location as students are assigned to it!', 'danger')
    else:
        db.session.delete(location)
        db.session.commit()
        flash('Location deleted successfully!', 'success')
    
    return redirect(url_for('admin.locations'))

@admin_bp.route('/card-requests')
@login_required
@admin_required
def card_requests():
    requests = CardRequest.query.order_by(CardRequest.request_date.desc()).all()
    return render_template('admin/dashboard.html', card_requests=requests, view_requests=True)

@admin_bp.route('/card-requests/<int:request_id>/<action>', methods=['POST'])
@login_required
@admin_required
def handle_card_request(request_id, action):
    card_request = CardRequest.query.get_or_404(request_id)
    student_profile = StudentProfile.query.filter_by(user_id=card_request.user_id).first()
    
    if action == 'approve':
        card_request.status = 'approved'
        card_request.approved_by = current_user.id
        card_request.approval_date = datetime.datetime.utcnow()
        
        if card_request.request_type == 'new':
            student_profile.card_status = 'active'
            # Generate a card number
            student_profile.card_number = f"CARD{student_profile.user_id}{datetime.datetime.utcnow().strftime('%y%m%d')}"
        elif card_request.request_type == 'cancel':
            student_profile.card_status = 'cancelled'
        elif card_request.request_type == 'replace':
            # Generate a new card number
            student_profile.card_number = f"CARD{student_profile.user_id}{datetime.datetime.utcnow().strftime('%y%m%d')}"
            student_profile.card_status = 'active'
        
        # Send notification to student
        notification = Notification(
            user_id=card_request.user_id,
            title='Card Request Approved',
            message=f'Your request to {card_request.request_type} card has been approved.',
            notification_type='card'
        )
        db.session.add(notification)
        
    elif action == 'reject':
        card_request.status = 'rejected'
        card_request.approved_by = current_user.id
        card_request.approval_date = datetime.datetime.utcnow()
        
        # Send notification to student
        notification = Notification(
            user_id=card_request.user_id,
            title='Card Request Rejected',
            message=f'Your request to {card_request.request_type} card has been rejected.',
            notification_type='card'
        )
        db.session.add(notification)
    
    db.session.commit()
    flash(f'Card request {action}d successfully!', 'success')
    return redirect(url_for('admin.card_requests'))

@admin_bp.route('/notifications', methods=['GET', 'POST'])
@login_required
@admin_required
def notifications():
    form = NotificationForm()
    # Get all users for the select field
    form.user_id.choices = [(u.id, f"{u.first_name} {u.last_name} ({u.username})") for u in User.query.all()]
    
    if form.validate_on_submit():
        if form.all_users.data:
            # Send to all users
            users = User.query.all()
            for user in users:
                notification = Notification(
                    user_id=user.id,
                    title=form.title.data,
                    message=form.message.data,
                    notification_type=form.notification_type.data
                )
                db.session.add(notification)
        else:
            # Send to specific user
            notification = Notification(
                user_id=form.user_id.data,
                title=form.title.data,
                message=form.message.data,
                notification_type=form.notification_type.data
            )
            db.session.add(notification)
        
        db.session.commit()
        flash('Notification sent successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/dashboard.html', form=form, title='Send Notification', send_notification=True)

@admin_bp.route('/student-profiles')
@login_required
@admin_required
def student_profiles():
    profiles = StudentProfile.query.join(User).all()
    return render_template('admin/dashboard.html', profiles=profiles, view_profiles=True)

@admin_bp.route('/student-profiles/<int:profile_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student_profile(profile_id):
    profile = StudentProfile.query.get_or_404(profile_id)
    form = UpdateCardStatusForm(obj=profile)
    
    if form.validate_on_submit():
        profile.card_status = form.card_status.data
        profile.fee_status = form.fee_status.data
        profile.current_dues = form.current_dues.data
        profile.fine_amount = form.fine_amount.data
        db.session.commit()
        
        # Send notification to student
        notification = Notification(
            user_id=profile.user_id,
            title='Profile Updated',
            message='Your bus card status has been updated by the administrator.',
            notification_type='card'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Student profile updated successfully!', 'success')
        return redirect(url_for('admin.student_profiles'))
    
    return render_template(
        'admin/dashboard.html', 
        form=form, 
        title='Edit Student Profile', 
        profile=profile,
        edit_profile=True
    )
