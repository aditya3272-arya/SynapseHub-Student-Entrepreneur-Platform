from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from routes.auth import login_required
from database import execute_single, execute_query, execute_insert, get_db_connection
from config import Config
from datetime import datetime
import os
import json
import sqlite3

profile_bp = Blueprint('profile', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@profile_bp.route('/upload_profile_pic', methods=['POST'])
@login_required
def upload_profile_pic():
    if 'profile_pic' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['profile_pic']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not (file and allowed_file(file.filename)):
        return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, and GIF files are allowed.'}), 400
    
    try:
        filename = secure_filename(f"profile_{session['user_id']}_{int(datetime.now().timestamp())}_{file.filename}")
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        file.save(filepath)
        
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT profile_image FROM users WHERE id = ?', (session['user_id'],))
        old_image = c.fetchone()
        
        c.execute('UPDATE users SET profile_image = ? WHERE id = ?', 
                 (filename, session['user_id']))
        conn.commit()
        
        if old_image and old_image[0] and old_image[0] != 'default-avatar.png':
            old_filepath = os.path.join(Config.UPLOAD_FOLDER, old_image[0])
            try:
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            except OSError:
                pass  
        
        conn.close()
        
        return jsonify({'success': True, 'filename': filename})
        
    except Exception as e:
        return jsonify({'error': f'Failed to upload image: {str(e)}'}), 500

@profile_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json()
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    age = data.get('age', '')
    skills = data.get('skills', '').strip()
    interests = data.get('interests', '').strip()
    bio = data.get('bio', '').strip()
    
    if not username or not email:
        return jsonify({'error': 'Username and email are required'}), 400
    
    if len(username) < 3 or len(username) > 50:
        return jsonify({'error': 'Username must be between 3 and 50 characters'}), 400
    
    if len(bio) > 500:
        return jsonify({'error': 'Bio must be less than 500 characters'}), 400
    
    if age and (not str(age).isdigit() or int(age) < 13 or int(age) > 25):
        return jsonify({'error': 'Age must be between 13 and 25'}), 400
    
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('''SELECT id FROM users WHERE (username = ? OR email = ?) AND id != ?''', 
                  (username, email, session['user_id']))
        if c.fetchone():
            conn.close()
            return jsonify({'error': 'Username or email already exists'}), 400
        
        c.execute('''SELECT username, email, age, skills, interests, bio 
                    FROM users WHERE id = ?''', (session['user_id'],))
        old_data = c.fetchone()
        
        c.execute('''UPDATE users SET 
                     username = ?, email = ?, age = ?, skills = ?, interests = ?, bio = ?
                     WHERE id = ?''',
                  (username, email, int(age) if age else None, skills, interests, bio, session['user_id']))
        
        updates_to_log = [
            ('username', old_data[0], username),
            ('email', old_data[1], email),
            ('age', old_data[2], age),
            ('skills', old_data[3], skills),
            ('interests', old_data[4], interests),
            ('bio', old_data[5], bio)
        ]
        
        for field, old_val, new_val in updates_to_log:
            if str(old_val or '') != str(new_val or ''):
                c.execute('''INSERT INTO profile_updates 
                            (user_id, field_updated, old_value, new_value)
                            VALUES (?, ?, ?, ?)''',
                         (session['user_id'], field, str(old_val or ''), str(new_val or '')))
        
        conn.commit()
        
        if old_data[0] != username:
            session['username'] = username
        
        conn.close()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
        
    except sqlite3.Error as e:
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': f'Update failed: {str(e)}'}), 500

@profile_bp.route('/profile')
@login_required
def profile():
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
        user = c.fetchone()
        
        if not user:
            conn.close()
            return redirect(url_for('auth.login'))
        
        c.execute('''SELECT id, title, problem_statement, category, created_date, 
                            view_count, like_count, comment_count, development_stage
                    FROM ideas WHERE user_id = ? ORDER BY created_date DESC''', 
                 (session['user_id'],))
        user_ideas = c.fetchall()
        
        c.execute('''
            SELECT i.title, t.team_id, COUNT(DISTINCT t2.member_username) as member_count,
                   CASE WHEN i.user_id = ? THEN 'Founder' ELSE 'Member' END as role,
                   i.category, t.joined_date
            FROM teams t 
            JOIN ideas i ON t.idea_id = i.id 
            LEFT JOIN teams t2 ON t.team_id = t2.team_id AND t2.status = 'active'
            WHERE t.member_username = ? AND t.status = 'active'
            GROUP BY t.team_id
            ORDER BY t.joined_date DESC
        ''', (session['user_id'], session['username']))
        user_teams = []
        for row in c.fetchall():
            user_teams.append({
                'idea_title': row[0],
                'team_id': row[1],
                'member_count': row[2],
                'role': row[3],
                'category': row[4],
                'joined_date': row[5]
            })
        
        c.execute('SELECT COUNT(*) FROM quiz_analytics WHERE user_id = ?', (session['user_id'],))
        total_quizzes = c.fetchone()[0]
        
        c.execute('SELECT AVG(accuracy) FROM quiz_analytics WHERE user_id = ?', (session['user_id'],))
        avg_accuracy = round(c.fetchone()[0] or 0, 1)
        
        c.execute('''SELECT accuracy FROM quiz_analytics WHERE user_id = ? 
                     ORDER BY quiz_date DESC LIMIT 10''', (session['user_id'],))
        recent_scores = [round(row[0]) for row in c.fetchall()]
        
        c.execute('''SELECT category, AVG(accuracy) as avg_acc
                    FROM quiz_analytics qa
                    JOIN quiz_questions qq ON json_extract(qa.questions_data, '$[0].category') = qq.category
                    WHERE qa.user_id = ? 
                    GROUP BY category 
                    ORDER BY avg_acc DESC LIMIT 1''', (session['user_id'],))
        best_category_result = c.fetchone()
        best_category = best_category_result[0] if best_category_result else 'Business Basics'
        
        improvement_rate = 0
        if len(recent_scores) >= 6:
            first_three = sum(recent_scores[-3:]) / 3 if len(recent_scores) >= 3 else 0
            last_three = sum(recent_scores[:3]) / 3 if len(recent_scores) >= 3 else 0
            if first_three > 0:
                improvement_rate = round(((last_three - first_three) / first_three) * 100, 1)
        
        total_likes_received = sum(idea[6] for idea in user_ideas)  
        total_views_received = sum(idea[5] for idea in user_ideas)  
        
        quiz_stats = {
            'total_quizzes': total_quizzes,
            'avg_accuracy': avg_accuracy,
            'best_category': best_category,
            'improvement_rate': max(0, improvement_rate),
            'recent_scores': recent_scores
        }
        
        user_stats = {
            'total_ideas': len(user_ideas),
            'total_teams': len(user_teams),
            'total_likes': total_likes_received,
            'total_views': total_views_received,
            'quiz_streak': user[9] if len(user) > 9 else 0, 
            'total_points': user[10] if len(user) > 10 else 0  
        }
        
        conn.close()
        
        return render_template('profile.html', 
                             user=user, 
                             user_ideas=user_ideas,
                             user_teams=user_teams,
                             teams_joined=len(user_teams),
                             quiz_stats=quiz_stats,
                             user_stats=user_stats)
                             
    except Exception as e:
        conn.close()
        return f"Error loading profile: {str(e)}", 500

@profile_bp.route('/delete_idea/<int:idea_id>', methods=['DELETE'])
@login_required
def delete_idea(idea_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('SELECT user_id, title FROM ideas WHERE id = ?', (idea_id,))
        result = c.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'error': 'Idea not found'}), 404
        
        if result[0] != session['user_id']:
            conn.close()
            return jsonify({'error': 'Unauthorized - You can only delete your own ideas'}), 403
        
        idea_title = result[1]
        
        
        c.execute('''DELETE FROM team_messages WHERE team_id IN 
                     (SELECT team_id FROM teams WHERE idea_id = ?)''', (idea_id,))
        
        c.execute('DELETE FROM teams WHERE idea_id = ?', (idea_id,))
        
        c.execute('DELETE FROM team_applications WHERE idea_id = ?', (idea_id,))
        
        c.execute('DELETE FROM idea_likes WHERE idea_id = ?', (idea_id,))
        
        c.execute('DELETE FROM comments WHERE idea_id = ?', (idea_id,))
        
        c.execute('DELETE FROM idea_evaluations WHERE idea_id = ?', (idea_id,))
        
        c.execute('DELETE FROM ideas WHERE id = ?', (idea_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Idea "{idea_title}" and all related data deleted successfully'
        })
        
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Deletion failed: {str(e)}'}), 500

@profile_bp.route('/get_profile_data')
@login_required
def get_profile_data():
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('''SELECT username, email, age, skills, interests, bio, profile_image, 
                            quiz_streak, total_points, join_date 
                    FROM users WHERE id = ?''', (session['user_id'],))
        user_data = c.fetchone()
        
        if not user_data:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        profile_data = {
            'username': user_data[0],
            'email': user_data[1],
            'age': user_data[2],
            'skills': user_data[3] or '',
            'interests': user_data[4] or '',
            'bio': user_data[5] or '',
            'profile_image': user_data[6] or 'default-avatar.png',
            'quiz_streak': user_data[7] or 0,
            'total_points': user_data[8] or 0,
            'join_date': user_data[9]
        }
        
        conn.close()
        return jsonify({'success': True, 'data': profile_data})
        
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Failed to load profile data: {str(e)}'}), 500

@profile_bp.route('/profile_history')
@login_required
def profile_history():
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('''SELECT field_updated, old_value, new_value, updated_date 
                    FROM profile_updates 
                    WHERE user_id = ? 
                    ORDER BY updated_date DESC LIMIT 50''', (session['user_id'],))
        
        history = []
        for row in c.fetchall():
            history.append({
                'field': row[0],
                'old_value': row[1],
                'new_value': row[2],
                'date': row[3]
            })
        
        conn.close()
        return jsonify({'success': True, 'history': history})
        
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Failed to load profile history: {str(e)}'}), 500

@profile_bp.route('/export_profile')
@login_required
def export_profile():
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
        user_data = c.fetchone()
        
        c.execute('SELECT * FROM ideas WHERE user_id = ?', (session['user_id'],))
        ideas_data = c.fetchall()
        
        c.execute('''SELECT c.comment_text, c.created_date, i.title 
                    FROM comments c 
                    JOIN ideas i ON c.idea_id = i.id 
                    WHERE c.user_id = ?''', (session['user_id'],))
        comments_data = c.fetchall()
        
        c.execute('SELECT * FROM quiz_analytics WHERE user_id = ?', (session['user_id'],))
        quiz_data = c.fetchall()
        
        export_data = {
            'user_profile': {
                'username': user_data[1],
                'email': user_data[2],
                'age': user_data[4],
                'skills': user_data[5],
                'interests': user_data[6],
                'bio': user_data[7],
                'join_date': user_data[9],
                'quiz_streak': user_data[10],
                'total_points': user_data[11]
            },
            'ideas_count': len(ideas_data),
            'comments_count': len(comments_data),
            'quizzes_taken': len(quiz_data),
            'export_date': datetime.now().isoformat()
        }
        
        conn.close()
        return jsonify({'success': True, 'data': export_data})
        
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Failed to export profile: {str(e)}'}), 500