from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extension import db
from my_models import User, StudentProfile, CardRequest, Payment, Notification, Location
from forms import StudentProfileForm, CardRequestForm, PaymentForm
from datetime import datetime

student_bp = Blueprint('student', __name__)

def student_required(f):
    """Decorator to check if user is student"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('You do not have permission to access this page!', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    # Get student profile
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    # Get recent payments
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.payment_date.desc()).limit(5).all()
    
    # Get unread notifications
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).limit(3).all()
    
    # Get pending card requests
    card_requests = CardRequest.query.filter_by(user_id=current_user.id, status='pending').all()
    
    return render_template(
        'student/dashboard.html',
        profile=profile,
        payments=payments,
        notifications=notifications,
        card_requests=card_requests
    )

@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    # Get student profile
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    # If profile doesn't exist, create one
    if not profile:
        profile = StudentProfile(user_id=current_user.id, student_id=f"STU{current_user.id:06d}")
        db.session.add(profile)
        db.session.commit()
    
    form = StudentProfileForm(obj=profile)
    
    # Get all locations for the select field
    locations = Location.query.filter_by(is_active=True).all()
    form.location_id.choices = [(l.id, l.name) for l in locations]
    
    if form.validate_on_submit():
        # Store the original values to check for changes
        original_department = profile.department
        original_year = profile.year
        original_semester = profile.semester
        original_location_id = profile.location_id
        
        # Update fields (student_id is not editable)
        profile.department = form.department.data
        profile.year = form.year.data
        profile.semester = form.semester.data
        profile.location_id = form.location_id.data
        
        # Check if any fields that require admin/accountant approval changed
        if (original_location_id != profile.location_id):
            # Create a notification for admins/accountants
            notification = Notification(
                user_id=1,  # Admin user (ID 1)
                title='Profile Change Request',
                message=f'Student {current_user.first_name} {current_user.last_name} ({profile.student_id}) has requested a location change.',
                notification_type='general'
            )
            db.session.add(notification)
            
            # Notify student about pending approval
            student_notification = Notification(
                user_id=current_user.id,
                title='Profile Change Request Submitted',
                message='Your profile change request has been submitted. You will be notified once it is reviewed.',
                notification_type='general'
            )
            db.session.add(student_notification)
            flash('Profile change request submitted. Changes will be applied after review.', 'info')
        else:
            # For non-critical changes that don't need approval
            flash('Profile updated successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('student.dashboard'))
    
    return render_template('student/profile.html', form=form, profile=profile)

@student_bp.route('/card-requests', methods=['GET', 'POST'])
@login_required
@student_required
def card_requests():
    # Get student profile for card status checking
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    form = CardRequestForm()
    
    # Determine if the student can request a new card
    can_request_new = False
    has_active_card = False
    
    if profile:
        has_active_card = profile.card_status == 'active'
        can_request_new = not has_active_card
    
    # Get all card requests for this student
    requests = CardRequest.query.filter_by(user_id=current_user.id).order_by(CardRequest.request_date.desc()).all()
    
    # Check for pending requests
    has_pending_request = any(request.status == 'pending' for request in requests)
    
    if form.validate_on_submit():
        # Additional validation check
        if form.request_type.data == 'new' and has_active_card:
            flash('You already have an active card. Please request to cancel or replace it instead.', 'warning')
        elif has_pending_request:
            flash('You already have a pending card request. Please wait for it to be processed.', 'warning')
        else:
            request = CardRequest(
                user_id=current_user.id,
                request_type=form.request_type.data,
                reason=form.reason.data,
                status='pending',
                request_date=datetime.utcnow()
            )
            db.session.add(request)
            
            # Add a notification for the admin
            notification = Notification(
                user_id=1,  # Admin user (ID 1)
                title='New Card Request',
                message=f'Student {current_user.first_name} {current_user.last_name} ({profile.student_id if profile else "N/A"}) has submitted a {form.request_type.data} card request.',
                notification_type='card'
            )
            db.session.add(notification)
            
            db.session.commit()
            flash('Card request submitted successfully!', 'success')
            return redirect(url_for('student.card_requests'))
    
    return render_template('student/card_requests.html', 
                          form=form, 
                          requests=requests, 
                          has_active_card=has_active_card,
                          can_request_new=can_request_new,
                          has_pending_request=has_pending_request,
                          profile=profile)

@student_bp.route('/payment', methods=['GET', 'POST'])
@login_required
@student_required
def payment():
    form = PaymentForm()
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    # Calculate pending amount if profile exists and has a location
    pending_amount = 0
    if profile and profile.location:
        # Base fee from location
        pending_amount = profile.location.fee_amount
        
        # Add any dues and fines
        if profile.current_dues:
            pending_amount += profile.current_dues
        if profile.fine_amount:
            pending_amount += profile.fine_amount
    
    if form.validate_on_submit():
        payment = Payment(
            user_id=current_user.id,
            amount=form.amount.data,
            payment_method=form.payment_method.data,
            description=form.description.data,
            academic_year=form.academic_year.data,
            semester=form.semester.data,
            payment_status='pending',
            transaction_id=f"TXN{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{current_user.id}"
        )
        db.session.add(payment)
        
        # For demo purposes, set the payment as successful immediately
        payment.payment_status = 'paid'
        payment.payment_date = datetime.utcnow()
        
        # Update student profile
        if profile:
            profile.fee_status = 'paid'
            profile.current_dues = 0
            profile.fine_amount = 0
            # Set fee due date to next semester (6 months from now)
            profile.fee_due_date = datetime.utcnow().replace(month=(datetime.utcnow().month + 6) % 12 or 12)
        
        # Add notification
        notification = Notification(
            user_id=current_user.id,
            title='Payment Successful',
            message=f'Your payment of ₹{form.amount.data} has been processed successfully.',
            notification_type='payment'
        )
        db.session.add(notification)
        
        db.session.commit()
        flash('Payment processed successfully!', 'success')
        return redirect(url_for('student.dashboard'))
    
    # Get payment history
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.payment_date.desc()).all()
    
    return render_template('student/payment.html', form=form, payments=payments, pending_amount=pending_amount)

@student_bp.route('/notifications')
@login_required
@student_required
def notifications():
    # Get all notifications for this student
    all_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # Mark all as read
    for notification in all_notifications:
        if not notification.is_read:
            notification.is_read = True
    
    db.session.commit()
    
    return render_template('student/notifications.html', notifications=all_notifications)

@student_bp.route('/notifications/read/<int:notification_id>')
@login_required
@student_required
def read_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    # Make sure the notification belongs to the current user
    if notification.user_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('student.dashboard'))
    
    notification.is_read = True
    db.session.commit()
    
    return redirect(url_for('student.notifications'))
