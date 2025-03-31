from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import User, StudentProfile, Payment, Notification, Location
from forms import UpdateCardStatusForm
from sqlalchemy import func
import datetime

accountant_bp = Blueprint('accountant', __name__)

def accountant_required(f):
    """Decorator to check if user is accountant or admin"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (current_user.role != 'accountant' and current_user.role != 'admin'):
            flash('You do not have permission to access this page!', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@accountant_bp.route('/dashboard')
@login_required
@accountant_required
def dashboard():
    # Get counts for dashboard stats
    total_students = User.query.filter_by(role='student').count()
    paid_students = StudentProfile.query.filter_by(fee_status='paid').count()
    pending_students = StudentProfile.query.filter_by(fee_status='pending').count()
    overdue_students = StudentProfile.query.filter_by(fee_status='overdue').count()
    
    # Get total fees collected
    total_fees = db.session.query(func.sum(Payment.amount)).filter(
        Payment.payment_status == 'paid'
    ).scalar() or 0
    
    # Get recent payments
    recent_payments = Payment.query.filter_by(payment_status='paid').order_by(Payment.payment_date.desc()).limit(10).all()
    
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
        'accountant/dashboard.html',
        total_students=total_students,
        paid_students=paid_students,
        pending_students=pending_students,
        overdue_students=overdue_students,
        total_fees=total_fees,
        monthly_payments=monthly_payments,
        payment_months=payment_months,
        recent_payments=recent_payments
    )

@accountant_bp.route('/students')
@login_required
@accountant_required
def students():
    # Get all student profiles
    profiles = StudentProfile.query.join(User).all()
    
    return render_template('accountant/manage_fees.html', profiles=profiles)

@accountant_bp.route('/students/<int:profile_id>', methods=['GET', 'POST'])
@login_required
@accountant_required
def update_student_fee(profile_id):
    profile = StudentProfile.query.get_or_404(profile_id)
    student = User.query.get(profile.user_id)
    
    form = UpdateCardStatusForm(obj=profile)
    
    if form.validate_on_submit():
        old_fee_status = profile.fee_status
        profile.fee_status = form.fee_status.data
        profile.current_dues = form.current_dues.data
        profile.fine_amount = form.fine_amount.data
        db.session.commit()
        
        # Send notification to student
        notification = Notification(
            user_id=profile.user_id,
            title='Fee Status Updated',
            message=f'Your fee status has been updated from {old_fee_status} to {profile.fee_status}.',
            notification_type='payment'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Student fee status updated successfully!', 'success')
        return redirect(url_for('accountant.students'))
    
    return render_template('accountant/manage_fees.html', form=form, student=student, profile=profile, update_student=True)

@accountant_bp.route('/payments')
@login_required
@accountant_required
def payments():
    # Get all payments
    payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    
    return render_template('accountant/dashboard.html', payments=payments, view_payments=True)

@accountant_bp.route('/payments/<int:payment_id>/update/<status>', methods=['POST'])
@login_required
@accountant_required
def update_payment_status(payment_id, status):
    payment = Payment.query.get_or_404(payment_id)
    
    if status in ['paid', 'pending', 'failed', 'refunded']:
        old_status = payment.payment_status
        payment.payment_status = status
        
        # Update student profile if payment is changed to paid
        if status == 'paid' and old_status != 'paid':
            profile = StudentProfile.query.filter_by(user_id=payment.user_id).first()
            if profile:
                profile.fee_status = 'paid'
                profile.current_dues = 0
                # Set fee due date to next semester (6 months from now)
                profile.fee_due_date = datetime.datetime.utcnow().replace(month=(datetime.datetime.utcnow().month + 6) % 12 or 12)
        
        db.session.commit()
        
        # Send notification to student
        notification = Notification(
            user_id=payment.user_id,
            title='Payment Status Updated',
            message=f'Your payment status has been updated from {old_status} to {status}.',
            notification_type='payment'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash(f'Payment status updated to {status} successfully!', 'success')
    else:
        flash('Invalid payment status!', 'danger')
    
    return redirect(url_for('accountant.payments'))

@accountant_bp.route('/location-fees')
@login_required
@accountant_required
def location_fees():
    # Get all locations
    locations = Location.query.all()
    
    return render_template('accountant/dashboard.html', locations=locations, view_locations=True)

@accountant_bp.route('/reports')
@login_required
@accountant_required
def reports():
    # Get fee collection per location
    location_fees = db.session.query(
        Location.name,
        func.count(StudentProfile.id).label('student_count'),
        func.sum(Location.fee_amount).label('total_fee')
    ).join(
        StudentProfile, Location.id == StudentProfile.location_id
    ).group_by(
        Location.name
    ).all()
    
    # Get fee status breakdown
    fee_status = db.session.query(
        StudentProfile.fee_status,
        func.count(StudentProfile.id).label('count')
    ).group_by(
        StudentProfile.fee_status
    ).all()
    
    # Get fee collection by month for current year
    current_year = datetime.datetime.utcnow().year
    monthly_collection = db.session.query(
        func.extract('month', Payment.payment_date).label('month'),
        func.sum(Payment.amount).label('amount')
    ).filter(
        func.extract('year', Payment.payment_date) == current_year,
        Payment.payment_status == 'paid'
    ).group_by(
        'month'
    ).all()
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_values = [0] * 12
    
    for month, amount in monthly_collection:
        month_values[int(month)-1] = float(amount)
    
    return render_template(
        'accountant/dashboard.html',
        location_fees=location_fees,
        fee_status=fee_status,
        months=months,
        month_values=month_values,
        view_reports=True
    )
