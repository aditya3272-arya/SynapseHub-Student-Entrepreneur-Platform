from flask import Blueprint, render_template, request, jsonify, session
from routes.auth import login_required
from database import execute_query, execute_single, execute_insert
from email_utils import send_team_application_email
import random
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for

team_bp = Blueprint('team', __name__)



@team_bp.route('/apply_to_team', methods=['POST'])
@login_required
def apply_to_team():
    idea_id = request.form.get('idea_id')
    message = request.form.get('message', '').strip()
    skills = request.form.get('skills', '').strip()
    experience = request.form.get('experience', '').strip()
    availability = request.form.get('availability', '').strip()
    
    username = session['username']
    
    if not idea_id or not message:
        return "Idea ID and message are required", 400
    
    existing_application = execute_single(
        'SELECT id FROM team_applications WHERE idea_id = ? AND applicant_username = ?', 
        (idea_id, username)
    )
    
    if existing_application:
        return "You have already applied to this team", 400
    
    idea_data = execute_single('''
        SELECT i.title, u.username, u.email 
        FROM ideas i JOIN users u ON i.user_id = u.id 
        WHERE i.id = ?
    ''', (idea_id,))
    
    if not idea_data:
        return "Idea not found", 404
    
    try:
        execute_insert('''
            INSERT INTO team_applications 
            (idea_id, applicant_username, message, skills, experience, availability, status, applied_date)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', datetime('now'))
        ''', (idea_id, username, message, skills, experience, availability))
        
        send_team_application_email(
            idea_data[2], idea_data[1], idea_data[0], username, message, skills
        )
        
        return "Application submitted successfully", 200
        
    except Exception as e:
        print(f"Error applying to team: {e}")
        return "Failed to submit application", 500

@team_bp.route('/approve_application/<application_id>')
def approve_application(application_id):
    parts = application_id.split('_')
    if len(parts) < 2:
        return "Invalid application ID", 400
    
    idea_title = '_'.join(parts[:-1]).replace('_', ' ')
    applicant_name = parts[-1]
    
    try:
        application = execute_single('''
            SELECT ta.id, ta.idea_id, i.title, i.user_id
            FROM team_applications ta
            JOIN ideas i ON ta.idea_id = i.id
            WHERE ta.applicant_username = ? AND i.title = ? AND ta.status = 'pending'
        ''', (applicant_name, idea_title))
        
        if not application:
            return "Application not found or already processed", 404
        
        execute_query(
            'UPDATE team_applications SET status = ? WHERE id = ?', 
            ('approved', application[0])
        )
        
        team_result = execute_single(
            'SELECT team_id FROM teams WHERE idea_id = ? AND is_founder = 1', 
            (application[1],)
        )
        
        if team_result:
            team_id = team_result[0]
            execute_insert('''
                INSERT INTO teams (team_id, idea_id, member_username, is_founder, status)
                VALUES (?, ?, ?, 0, 'active')
            ''', (team_id, application[1], applicant_name))
        
        return f"Application approved! {applicant_name} has been added to the team for '{idea_title}'"
        
    except Exception as e:
        print(f"Error approving application: {e}")
        return "Failed to approve application", 500

@team_bp.route('/api/team_messages/<int:team_id>')
@login_required
def get_team_messages(team_id):
    member_check = execute_single(
        'SELECT 1 FROM teams WHERE team_id = ? AND member_username = ?', 
        (team_id, session['username'])
    )
    
    if not member_check:
        return jsonify([]), 403
    
    try:
        messages_data = execute_query('''
            SELECT username, message, timestamp 
            FROM team_messages 
            WHERE team_id = ? 
            ORDER BY timestamp ASC
        ''', (team_id,))
        
        messages = [
            {'username': r[0], 'message': r[1], 'timestamp': r[2]} 
            for r in messages_data
        ]
        
        return jsonify(messages)
        
    except Exception as e:
        print(f"Error getting team messages: {e}")
        return jsonify([]), 500

@team_bp.route('/api/send_team_message', methods=['POST'])
@login_required
def send_team_message():
    data = request.get_json()
    team_id = data.get('team_id')
    message = data.get('message', '').strip()
    username = session['username']
    
    if not team_id or not message:
        return "Team ID and message are required", 400
    
    member_check = execute_single(
        'SELECT 1 FROM teams WHERE team_id = ? AND member_username = ?', 
        (team_id, username)
    )
    
    if not member_check:
        return "Forbidden", 403
    
    try:
        execute_insert('''
            INSERT INTO team_messages (team_id, username, message, timestamp)
            VALUES (?, ?, ?, datetime('now'))
        ''', (team_id, username, message))
        
        return "Message sent", 200
        
    except Exception as e:
        print(f"Error sending team message: {e}")
        return "Failed to send message", 500

@team_bp.route('/leave_team/<int:team_id>', methods=['POST'])
@login_required
def leave_team(team_id):
    username = session['username']
    
    try:
        execute_query(
            'DELETE FROM teams WHERE team_id = ? AND member_username = ?', 
            (team_id, username)
        )
        
        return "Left team successfully", 200
        
    except Exception as e:
        print(f"Error leaving team: {e}")
        return "Failed to leave team", 500