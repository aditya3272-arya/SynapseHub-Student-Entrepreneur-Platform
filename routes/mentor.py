from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from database import execute_query, execute_single, execute_insert
from email_utils import send_booking_confirmation_email, generate_meeting_link
import uuid

mentor_bp = Blueprint('mentor', __name__)

@mentor_bp.route('/book_session', methods=['POST'])
@login_required

def book_session():
    data = request.get_json()
    
    mentor_id = data.get('mentor_id')
    mentor_name = data.get('mentor_name')
    student_name = data.get('student_name', '').strip()
    student_email = data.get('student_email', '').strip()
    session_date = data.get('session_date')
    session_time = data.get('session_time')
    session_topic = data.get('session_topic', '').strip()
    
    if not all([mentor_id, mentor_name, student_name, student_email, session_date, session_time]):
        return jsonify({'error': 'All fields are required'}), 400
    
    if '@' not in student_email or '.' not in student_email:
        return jsonify({'error': 'Please enter a valid email address'}), 400
    
    meeting_link = generate_meeting_link()
    
    try:
        booking_id = execute_insert('''
            INSERT INTO session_bookings 
            (user_id, mentor_id, student_name, student_email, session_date, 
             session_time, session_topic, meeting_link, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'confirmed')
        ''', (session['user_id'], mentor_id, student_name, student_email,
              session_date, session_time, session_topic, meeting_link))
        
        send_booking_confirmation_email(
            student_email, student_name, mentor_name,
            session_date, session_time, session_topic, meeting_link
        )
        
        return jsonify({
            'success': True, 
            'booking_id': booking_id,
            'message': 'Session booked successfully! Check your email for details.'
        })
        
    except Exception as e:
        print(f"Booking error: {e}")
        return jsonify({'error': 'Failed to book session. Please try again.'}), 500

@mentor_bp.route('/my_bookings')
@login_required
def my_bookings():
    try:
        bookings_data = execute_query('''
            SELECT sb.id, sb.mentor_id, m.name as mentor_name, sb.session_date, 
                   sb.session_time, sb.session_topic, sb.meeting_link, sb.status,
                   sb.created_date
            FROM session_bookings sb
            JOIN mentors m ON sb.mentor_id = m.id
            WHERE sb.user_id = ?
            ORDER BY sb.session_date DESC, sb.session_time DESC
        ''', (session['user_id'],))
        
        bookings = []
        for row in bookings_data:
            bookings.append({
                'id': row[0],
                'mentor_id': row[1],
                'mentor_name': row[2],
                'session_date': row[3],
                'session_time': row[4],
                'session_topic': row[5] or 'General mentorship discussion',
                'meeting_link': row[6],
                'status': row[7],
                'created_date': row[8]
            })
        
        return jsonify(bookings)
        
    except Exception as e:
        print(f"Error getting bookings: {e}")
        return jsonify([]), 500

@mentor_bp.route('/cancel_booking/<int:booking_id>', methods=['DELETE'])
@login_required
def cancel_booking(booking_id):
    try:
        booking = execute_single(
            'SELECT user_id, status FROM session_bookings WHERE id = ?', 
            (booking_id,)
        )
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        if booking[0] != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if booking[1] == 'cancelled':
            return jsonify({'error': 'Booking already cancelled'}), 400
        
        execute_query(
            'UPDATE session_bookings SET status = ? WHERE id = ?', 
            ('cancelled', booking_id)
        )
        
        return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
        
    except Exception as e:
        print(f"Error cancelling booking: {e}")
        return jsonify({'error': 'Failed to cancel booking'}), 500

@mentor_bp.route('/reschedule_booking/<int:booking_id>', methods=['PUT'])
@login_required
def reschedule_booking(booking_id):
    data = request.get_json()
    new_date = data.get('session_date')
    new_time = data.get('session_time')
    
    if not new_date or not new_time:
        return jsonify({'error': 'New date and time are required'}), 400
    
    try:
        booking = execute_single(
            'SELECT user_id, status FROM session_bookings WHERE id = ?', 
            (booking_id,)
        )
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        if booking[0] != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if booking[1] == 'cancelled':
            return jsonify({'error': 'Cannot reschedule cancelled booking'}), 400
        
        execute_query('''
            UPDATE session_bookings 
            SET session_date = ?, session_time = ?, status = 'rescheduled'
            WHERE id = ?
        ''', (new_date, new_time, booking_id))
        
        return jsonify({'success': True, 'message': 'Booking rescheduled successfully'})
        
    except Exception as e:
        print(f"Error rescheduling booking: {e}")
        return jsonify({'error': 'Failed to reschedule booking'}), 500

@mentor_bp.route('/mentor_feedback/<int:booking_id>', methods=['POST'])
@login_required
def submit_mentor_feedback(booking_id):
    data = request.get_json()
    rating = data.get('rating')
    feedback = data.get('feedback', '').strip()
    
    if not rating or rating < 1 or rating > 5:
        return jsonify({'error': 'Please provide a rating between 1 and 5'}), 400
    
    try:
        booking = execute_single('''
            SELECT user_id, mentor_id, status FROM session_bookings WHERE id = ?
        ''', (booking_id,))
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        if booking[0] != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        execute_query('''
            CREATE TABLE IF NOT EXISTS session_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER,
                user_id INTEGER,
                mentor_id INTEGER,
                rating INTEGER,
                feedback TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (booking_id) REFERENCES session_bookings (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (mentor_id) REFERENCES mentors (id)
            )
        ''')
        
        execute_insert('''
            INSERT INTO session_feedback 
            (booking_id, user_id, mentor_id, rating, feedback)
            VALUES (?, ?, ?, ?, ?)
        ''', (booking_id, session['user_id'], booking[1], rating, feedback))
        

                
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        return jsonify({'error': 'Failed to submit feedback'}), 500

@mentor_bp.route('/available_slots/<int:mentor_id>')
@login_required
def get_available_slots(mentor_id):
    try:
        
        mentor = execute_single(
            'SELECT availability FROM mentors WHERE id = ?', 
            (mentor_id,)
        )
        
        if not mentor:
            return jsonify({'error': 'Mentor not found'}), 404
        
        available_slots = [
            {'date': '2024-01-15', 'time': '10:00 AM'},
            {'date': '2024-01-15', 'time': '2:00 PM'},
            {'date': '2024-01-16', 'time': '11:00 AM'},
            {'date': '2024-01-17', 'time': '3:00 PM'},
            {'date': '2024-01-18', 'time': '10:00 AM'}
        ]
        
        return jsonify({
            'availability': mentor[0],
            'slots': available_slots
        })
        
    except Exception as e:
        print(f"Error getting available slots: {e}")
        return jsonify({'error': 'Failed to get available slots'}), 500