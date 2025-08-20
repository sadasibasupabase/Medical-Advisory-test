from flask import render_template, request, jsonify, session, redirect, url_for, flash
from app import app, db
from models import User, Chat, Symptom, TreatmentSummary, ResearchPaper, Reminder
from medical_ai import analyze_symptoms, generate_treatment_summary, research_query, patient_engagement_response
from datetime import datetime, timedelta
import json

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Chat interface for symptom analysis and patient engagement"""
    # Initialize session user if not exists
    if 'user_id' not in session:
        session['user_id'] = 1  # Default user for demo
        session['user_name'] = 'Demo User'
        session['user_role'] = 'patient'
        
        # Create user if doesn't exist
        user = User.query.get(1)
        if not user:
            user = User(id=1, name='Demo User', role='patient')
            db.session.add(user)
            db.session.commit()
    
    # Get recent chat history
    recent_chats = Chat.query.filter_by(user_id=session['user_id']).order_by(Chat.timestamp.desc()).limit(20).all()
    recent_chats.reverse()  # Show oldest first
    
    return render_template('chat.html', recent_chats=recent_chats)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Handle chat messages and return AI responses"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        model = data.get('model', 'gpt-5-mini')
        # model ='gpt-5-mini'
        chat_type = data.get('type', 'general')  # symptom, exercise, followup, general
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
            
        user_id = session.get('user_id', 1)
        
        # Generate response based on chat type
        if chat_type == 'symptom':
            result = analyze_symptoms(message, model)
            response_text = result['response']
            
            # Save symptom record
            symptom = Symptom(
                user_id=user_id,
                description=message,
                triage_level=result.get('triage_level', 'monitor')
            )
            db.session.add(symptom)
            
        elif chat_type == 'exercise':
            response_text = patient_engagement_response(message, 'exercise', model)
        elif chat_type == 'followup':
            response_text = patient_engagement_response(message, 'followup', model)
        else:
            response_text = patient_engagement_response(message, 'general', model)
        
        # Save chat record
        chat = Chat(
            user_id=user_id,
            message=message,
            response=response_text,
            model=model
        )
        db.session.add(chat)
        db.session.commit()
        
        return jsonify({
            'response': response_text,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"Chat API error: {str(e)}")
        return jsonify({'error': 'Sorry, I encountered an error. Please try again.'}), 500

@app.route('/research')
def research():
    """Research portal for doctors"""
    if session.get('user_role') != 'doctor':
        # Allow demo access
        session['user_role'] = 'doctor'
        session['user_name'] = 'Dr. Demo'
    
    papers = ResearchPaper.query.order_by(ResearchPaper.created_at.desc()).limit(10).all()
    return render_template('research.html', papers=papers)

@app.route('/api/upload_paper', methods=['POST'])
def upload_paper():
    """Upload research paper"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400
        
        user_id = session.get('user_id', 1)
        
        paper = ResearchPaper(
            title=title,
            content=content,
            uploaded_by=user_id
        )
        db.session.add(paper)
        db.session.commit()
        
        return jsonify({'message': 'Paper uploaded successfully', 'paper_id': paper.id})
        
    except Exception as e:
        app.logger.error(f"Upload paper error: {str(e)}")
        return jsonify({'error': 'Failed to upload paper'}), 500

@app.route('/api/research_query', methods=['POST'])
def api_research_query():
    """Query research papers"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        model = data.get('model', 'gpt-4o')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Get all research papers content
        papers = ResearchPaper.query.all()
        papers_content = "\n\n".join([f"Title: {p.title}\nContent: {p.content}" for p in papers])
        
        if not papers_content:
            return jsonify({'response': 'No research papers available. Please upload some papers first.'})
        
        response = research_query(query, papers_content, model)
        
        return jsonify({
            'response': response,
            'papers_count': len(papers)
        })
        
    except Exception as e:
        app.logger.error(f"Research query error: {str(e)}")
        return jsonify({'error': 'Failed to process research query'}), 500

@app.route('/api/generate_summary', methods=['POST'])
def generate_summary():
    """Generate treatment summary"""
    try:
        data = request.get_json()
        notes = data.get('notes', '').strip()
        language = data.get('language', 'en')
        model = data.get('model', 'gpt-4o')
        
        if not notes:
            return jsonify({'error': 'Discharge notes are required'}), 400
        
        summary = generate_treatment_summary(notes, language, model)
        
        # Save summary
        treatment_summary = TreatmentSummary(
            patient_id=session.get('user_id', 1),
            doctor_id=session.get('user_id', 1),
            original_notes=notes,
            summary_text=summary,
            language=language
        )
        db.session.add(treatment_summary)
        db.session.commit()
        
        return jsonify({
            'summary': summary,
            'summary_id': treatment_summary.id
        })
        
    except Exception as e:
        app.logger.error(f"Generate summary error: {str(e)}")
        return jsonify({'error': 'Failed to generate summary'}), 500

@app.route('/reminders')
def reminders():
    """Medication and appointment reminders"""
    user_id = session.get('user_id', 1)
    upcoming_reminders = Reminder.query.filter(
        Reminder.user_id == user_id,
        Reminder.status == 'active',
        Reminder.schedule_time >= datetime.now()
    ).order_by(Reminder.schedule_time).limit(10).all()
    
    return render_template('reminders.html', reminders=upcoming_reminders)

@app.route('/api/add_reminder', methods=['POST'])
def add_reminder():
    """Add a new reminder"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '')
        reminder_type = data.get('type', 'medication')
        schedule_time = data.get('schedule_time')
        
        if not title or not schedule_time:
            return jsonify({'error': 'Title and schedule time are required'}), 400
        
        # Parse schedule time
        schedule_dt = datetime.fromisoformat(schedule_time)
        
        reminder = Reminder(
            user_id=session.get('user_id', 1),
            type=reminder_type,
            title=title,
            description=description,
            schedule_time=schedule_dt
        )
        db.session.add(reminder)
        db.session.commit()
        
        return jsonify({'message': 'Reminder added successfully', 'reminder_id': reminder.id})
        
    except Exception as e:
        app.logger.error(f"Add reminder error: {str(e)}")
        return jsonify({'error': 'Failed to add reminder'}), 500

@app.route('/switch_role/<role>')
def switch_role(role):
    """Switch between patient and doctor roles for demo"""
    if role in ['patient', 'doctor']:
        session['user_role'] = role
        session['user_name'] = 'Dr. Demo' if role == 'doctor' else 'Demo Patient'
        flash(f'Switched to {role} role', 'success')
    return redirect(request.referrer or url_for('index'))
