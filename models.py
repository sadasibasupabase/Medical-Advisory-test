from app import db
from datetime import datetime
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')  # patient/doctor
    preferred_language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    chats = db.relationship('Chat', backref='user', lazy=True)
    symptoms = db.relationship('Symptom', backref='user', lazy=True)
    reminders = db.relationship('Reminder', backref='user', lazy=True)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    model = db.Column(db.String(20), default='gpt-5-mini')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Symptom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    triage_level = db.Column(db.String(20))  # urgent, monitor, mild
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TreatmentSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    original_notes = db.Column(db.Text, nullable=False)
    summary_text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('User', foreign_keys=[patient_id], backref='treatment_summaries')
    doctor = db.relationship('User', foreign_keys=[doctor_id])

class ResearchPaper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    uploader = db.relationship('User', backref='research_papers')

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # medication, exercise, appointment
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    schedule_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
