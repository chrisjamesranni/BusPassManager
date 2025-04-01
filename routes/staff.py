from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extension import db
from my_models import User, StudentProfile, BusEntry, Location
from forms import QRScanForm, UpdateCardStatusForm, UserForm, StudentProfileForm
from werkzeug.security import generate_password_hash
import datetime

staff_bp = Blueprint('staff', __name__)

def staff_required(f):
    """Decorator to check if user is staff or admin"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (current_user.role != 'staff' and current_user.role != 'admin'):
            flash('You do not have permission to access this page!', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@staff_bp.route('/scan', methods=['GET', 'POST'])
@login_required
@staff_required
def scan():
    form = QRScanForm()
    
    if form.validate_on_submit():
        student_id = form.student_id.data
        return redirect(url_for('staff.check_student', student_id=student_id))
    
    return render_template('staff/scan.html', form=form)

@staff_bp.route('/scan-api', methods=['POST'])
@login_required
@staff_required
def scan_api():
    """API endpoint for handling AJAX requests from QR scanner"""
    data = request.json
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({'success': False, 'message': 'No student ID provided'}), 400
    
    # Find the student profile
    profile = StudentProfile.query.filter_by(student_id=student_id).first()
    
    if not profile:
        return jsonify({'success': False, 'message': 'Student not found'}), 404
    
    # Get student information
    student = User.query.get(profile.user_id)
    
    # Get location information
    location_name = "Unknown"
    if profile.location:
        location_name = profile.location.name
    
    # Create response with student details
    response = {
        'success': True,
        'student': {
            'id': student.id,
            'name': f"{student.first_name} {student.last_name}",
            'student_id': profile.student_id,
            'card_status': profile.card_status,
            'fee_status': profile.fee_status,
            'location': location_name,
            'current_dues': profile.current_dues,
            'fine_amount': profile.fine_amount
        }
    }
    
    return jsonify(response)

@staff_bp.route('/check-student/<student_id>')
@login_required
@staff_required
def check_student(student_id):
    # Find the student profile
    profile = StudentProfile.query.filter_by(student_id=student_id).first()
    
    if not profile:
        flash('Student not found!', 'danger')
        return redirect(url_for('staff.scan'))
    
    # Get student information
    student = User.query.get(profile.user_id)
    
    # Record bus entry
    entry = BusEntry(
        student_profile_id=profile.id,
        staff_id=current_user.id,
        bus_number=request.args.get('bus_number', 'Unknown'),
        route=request.args.get('route', 'Unknown')
    )
    db.session.add(entry)
    db.session.commit()
    
    return render_template('staff/student_details.html', student=student, profile=profile)

@staff_bp.route('/recent-entries')
@login_required
@staff_required
def recent_entries():
    # Get recent entries from this staff member
    entries = BusEntry.query.filter_by(staff_id=current_user.id).order_by(BusEntry.entry_time.desc()).limit(50).all()
    
    return render_template('staff/scan.html', entries=entries, view_entries=True)

@staff_bp.route('/entry-stats')
@login_required
@staff_required
def entry_stats():
    # Get today's entries count
    today = datetime.datetime.utcnow().date()
    today_entries = BusEntry.query.filter(
        BusEntry.staff_id == current_user.id,
        BusEntry.entry_time >= today
    ).count()
    
    # Get this week's entries count
    week_start = today - datetime.timedelta(days=today.weekday())
    week_entries = BusEntry.query.filter(
        BusEntry.staff_id == current_user.id,
        BusEntry.entry_time >= week_start
    ).count()
    
    # Get this month's entries count
    month_start = datetime.datetime(today.year, today.month, 1)
    month_entries = BusEntry.query.filter(
        BusEntry.staff_id == current_user.id,
        BusEntry.entry_time >= month_start
    ).count()
    
    return render_template(
        'staff/scan.html', 
        today_entries=today_entries,
        week_entries=week_entries,
        month_entries=month_entries,
        view_stats=True
    )

@staff_bp.route('/add-student', methods=['GET', 'POST'])
@login_required
@staff_required
def add_student():
    """Add a new student to the system"""
    user_form = UserForm()
    profile_form = StudentProfileForm()
    
    # Get all available locations for the dropdown
    locations = Location.query.filter_by(is_active=True).all()
    profile_form.location_id.choices = [(l.id, l.name) for l in locations]
    
    if user_form.validate_on_submit() and profile_form.validate_on_submit():
        # First create the user
        hashed_password = generate_password_hash(user_form.password.data)
        user = User(
            username=user_form.username.data,
            email=user_form.email.data,
            password_hash=hashed_password,
            first_name=user_form.first_name.data,
            last_name=user_form.last_name.data,
            phone=user_form.phone.data,
            role='student',
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        
        # Then create the student profile
        student_profile = StudentProfile(
            user_id=user.id,
            student_id=profile_form.student_id.data,
            department=profile_form.department.data,
            year=profile_form.year.data,
            semester=profile_form.semester.data,
            location_id=profile_form.location_id.data,
            card_status='pending'  # New students start with pending card status
        )
        db.session.add(student_profile)
        db.session.commit()
        
        flash('Student added successfully!', 'success')
        return redirect(url_for('staff.check_student', student_id=student_profile.student_id))
    
    return render_template('staff/add_student.html', 
                          user_form=user_form, 
                          profile_form=profile_form,
                          title='Add New Student')
