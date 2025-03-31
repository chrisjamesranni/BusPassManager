from datetime import datetime
from flask_login import UserMixin
from app import db
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum

class Role(enum.Enum):
    admin = "admin"
    staff = "staff"
    accountant = "accountant"
    student = "student"

class CardStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    pending = "pending"
    cancelled = "cancelled"
    expired = "expired"

class PaymentStatus(enum.Enum):
    paid = "paid"
    pending = "pending"
    failed = "failed"
    refunded = "refunded"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False, default='student')
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    payments = relationship("Payment", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    card_requests = relationship("CardRequest", back_populates="user", foreign_keys="CardRequest.user_id")
    
    def __repr__(self):
        return f'<User {self.username}>'

class Location(db.Model):
    __tablename__ = 'locations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255))
    distance = Column(Float)  # Distance from college in km
    fee_amount = Column(Float, nullable=False)  # Base fee for this location
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student_profiles = relationship("StudentProfile", back_populates="location")
    
    def __repr__(self):
        return f'<Location {self.name}>'

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    student_id = Column(String(20), unique=True, nullable=False)  # College student ID
    department = Column(String(100))
    year = Column(Integer)
    semester = Column(Integer)
    location_id = Column(Integer, ForeignKey('locations.id'))
    card_status = Column(String(20), default='inactive')
    card_number = Column(String(20), unique=True)
    qr_code = Column(String(255))  # URL or data for QR code
    fee_status = Column(String(20), default='pending')
    fee_due_date = Column(DateTime)
    current_dues = Column(Float, default=0.0)
    fine_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="student_profile")
    location = relationship("Location", back_populates="student_profiles")
    
    def __repr__(self):
        return f'<StudentProfile {self.student_id}>'

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    payment_method = Column(String(50))
    transaction_id = Column(String(100))
    payment_status = Column(String(20), default='pending')
    description = Column(String(255))
    academic_year = Column(String(20))
    semester = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.amount}>'

class CardRequest(db.Model):
    __tablename__ = 'card_requests'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    request_type = Column(String(20), nullable=False)  # new, cancel, replace
    reason = Column(Text)
    status = Column(String(20), default='pending')  # pending, approved, rejected
    approved_by = Column(Integer, ForeignKey('users.id'))
    request_date = Column(DateTime, default=datetime.utcnow)
    approval_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="card_requests", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approved_by], primaryjoin="CardRequest.approved_by == User.id")
    
    def __repr__(self):
        return f'<CardRequest {self.id} - {self.request_type}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    notification_type = Column(String(50))  # payment, card, general
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.title}>'

class BusEntry(db.Model):
    __tablename__ = 'bus_entries'
    
    id = Column(Integer, primary_key=True)
    student_profile_id = Column(Integer, ForeignKey('student_profiles.id'), nullable=False)
    staff_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    entry_time = Column(DateTime, default=datetime.utcnow)
    bus_number = Column(String(20))
    route = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student_profile = relationship("StudentProfile")
    staff = relationship("User", foreign_keys=[staff_id])
    
    def __repr__(self):
        return f'<BusEntry {self.id}>'
