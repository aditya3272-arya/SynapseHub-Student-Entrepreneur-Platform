from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from database import execute_query, execute_single, execute_insert
from datetime import datetime
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/idea/<int:idea_id>')
@login_required
def get_idea(idea_id):
    try:
        idea_data = execute_single('''SELECT 
                        i.id,
                        COALESCE(i.title, '') as title,
                        COALESCE(i.problem_statement, '') as problem_statement,
                        COALESCE(i.solution_description, '') as solution_description,
                        COALESCE(i.category, 'General') as category,
                        COALESCE(i.created_date, datetime('now')) as created_date,
                        COALESCE(i.view_count, 0) as view_count,
                        COALESCE(i.like_count, 0) as like_count,
                        COALESCE(u.username, 'Unknown') as username,
                        COALESCE(i.development_stage, 'Idea') as development_stage,
                        COALESCE(i.target_market, '') as target_market,
                        COALESCE(i.budget_range, '') as budget_range,
                        COALESCE(i.timeline, '') as timeline,
                        COALESCE(i.tags, '') as tags,
                        COALESCE(i.comment_count, 0) as comment_count,
                        COALESCE(i.team_needs, '') as team_needs,
                        COALESCE(i.inspiration, '') as inspiration,
                        COALESCE(i.open_collaboration, 0) as open_collaboration
                   FROM ideas i 
                   LEFT JOIN users u ON i.user_id = u.id 
                   WHERE i.id = ? AND COALESCE(i.status, 'active') = 'active' ''', (idea_id,))
        
        if not idea_data:
            return jsonify({'error': 'Idea not found'}), 404
            
        return jsonify({
            'id': idea_data[0],
            'title': idea_data[1],
            'problem_statement': idea_data[2],
            'solution_description': idea_data[3],
            'category': idea_data[4],
            'created_date': idea_data[5],
            'view_count': idea_data[6],
            'like_count': idea_data[7],
            'username': idea_data[8],
            'development_stage': idea_data[9],
            'target_market': idea_data[10],
            'budget_range': idea_data[11],
            'timeline': idea_data[12],
            'tags': idea_data[13],
            'comment_count': idea_data[14],
            'team_needs': idea_data[15],
            'inspiration': idea_data[16],
            'open_collaboration': idea_data[17]
        })
        
    except Exception as e:
        print(f"Error fetching idea: {e}")
        return jsonify({'error': 'Failed to fetch idea'}), 500

@api_bp.route('/api/comments/<int:idea_id>')
@login_required
def get_comments(idea_id):
    idea_check = execute_single('SELECT id FROM ideas WHERE id = ?', (idea_id,))
    if not idea_check:
        return jsonify({'error': 'Idea not found'}), 404
    
    try:
        comments_data = execute_query('''
            SELECT c.comment_text, c.created_date, u.username 
            FROM comments c 
            JOIN users u ON c.user_id = u.id 
            WHERE c.idea_id = ? 
            ORDER BY c.created_date DESC
        ''', (idea_id,))
        
        comments = []
        for row in comments_data:
            comments.append({
                'text': row[0],
                'date': row[1],
                'author': row[2]
            })
        
        return jsonify(comments)
        
    except Exception as e:
        print(f"Error getting comments: {e}")
        return jsonify({'error': 'Failed to load comments'}), 500

@api_bp.route('/api/comments', methods=['POST'])
@login_required
def post_comment():
    data = request.get_json()
    idea_id = data.get('idea_id')
    comment_text = data.get('text', '').strip()
    
    if not comment_text:
        return jsonify({'error': 'Comment text is required'}), 400
    
    idea_data = execute_single('SELECT id, comment_count FROM ideas WHERE id = ?', (idea_id,))
    if not idea_data:
        return jsonify({'error': 'Idea not found'}), 404
    
    current_comment_count = idea_data[1] or 0
    
    try:
        execute_insert('''
            INSERT INTO comments (idea_id, user_id, comment_text) 
            VALUES (?, ?, ?)
        ''', (idea_id, session['user_id'], comment_text))
        
        new_count = current_comment_count + 1
        execute_query('UPDATE ideas SET comment_count = ? WHERE id = ?', (new_count, idea_id))
        
        username = execute_single('SELECT username FROM users WHERE id = ?', (session['user_id'],))[0]
        
        return jsonify({
            'text': comment_text,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'author': username
        })
        
    except Exception as e:
        print(f"Error posting comment: {e}")
        return jsonify({'error': 'Failed to post comment'}), 500

@api_bp.route('/like_idea/<int:idea_id>', methods=['POST'])
@login_required
def like_idea(idea_id):
    idea_data = execute_single('SELECT id, like_count FROM ideas WHERE id = ?', (idea_id,))
    if not idea_data:
        return jsonify({'error': 'Idea not found'}), 404
    
    current_like_count = idea_data[1] or 0
    
    try:
        existing_like = execute_single(
            'SELECT id FROM idea_likes WHERE user_id = ? AND idea_id = ?', 
            (session['user_id'], idea_id)
        )
        
        if existing_like:
            execute_query(
                'DELETE FROM idea_likes WHERE user_id = ? AND idea_id = ?', 
                (session['user_id'], idea_id)
            )
            new_count = max(0, current_like_count - 1)
            execute_query('UPDATE ideas SET like_count = ? WHERE id = ?', (new_count, idea_id))
            liked = False
        else:
            execute_insert(
                'INSERT INTO idea_likes (user_id, idea_id) VALUES (?, ?)', 
                (session['user_id'], idea_id)
            )
            new_count = current_like_count + 1
            execute_query('UPDATE ideas SET like_count = ? WHERE id = ?', (new_count, idea_id))
            liked = True

        return jsonify({'liked': liked, 'like_count': new_count})
        
    except Exception as e:
        print(f"Error toggling like: {e}")
        return jsonify({'error': 'Failed to update like status'}), 500

@api_bp.route('/api/user_likes')
@login_required
def get_user_likes():
    try:
        liked_ideas_data = execute_query(
            'SELECT idea_id FROM idea_likes WHERE user_id = ?', 
            (session['user_id'],)
        )
        liked_ideas = [row[0] for row in liked_ideas_data]
        
        return jsonify(liked_ideas)
        
    except Exception as e:
        print(f"Error getting user likes: {e}")
        return jsonify([]), 500

@api_bp.route('/api/increment_view/<int:idea_id>', methods=['POST'])
@login_required
def increment_view(idea_id):
    try:
        result = execute_single('SELECT view_count FROM ideas WHERE id = ?', (idea_id,))
        
        if result:
            current_views = result[0] or 0
            new_views = current_views + 1
            execute_query('UPDATE ideas SET view_count = ? WHERE id = ?', (new_views, idea_id))
            return jsonify({'success': True, 'views': new_views})
        
        return jsonify({'error': 'Idea not found'}), 404
        
    except Exception as e:
        print(f"Error incrementing view: {e}")
        return jsonify({'error': 'Failed to update view count'}), 500

@api_bp.route('/get_daily_quiz')
@login_required
def get_daily_quiz():
    completed_today = execute_single('''
        SELECT id FROM quiz_analytics 
        WHERE user_id = ? AND quiz_date = DATE('now')
    ''', (session['user_id'],))
    
    if completed_today:
        return jsonify({'questions': []})
    
    try:
        questions_data = execute_query('SELECT * FROM quiz_questions ORDER BY RANDOM() LIMIT 15')
        
        quiz_questions = []
        for q in questions_data:
            quiz_questions.append({
                'id': q[0],
                'question': q[1],
                'options': json.loads(q[2]),
                'correct_answer': q[3],
                'explanation': q[4] if q[4] else 'Great job!',
                'category': q[5] if q[5] else 'General'
            })
        
        return jsonify({'questions': quiz_questions})
        
    except Exception as e:
        print(f"Error getting quiz questions: {e}")
        return jsonify({'questions': []}), 500

@api_bp.route('/submit_quiz_answer', methods=['POST'])
@login_required
def submit_quiz_answer():
    return jsonify({'status': 'success'})

@api_bp.route('/update_quiz_stats', methods=['POST'])
@login_required
def update_quiz_stats():
    data = request.get_json()
    questions_answered = data.get('questions_answered', 0)
    correct_answers = data.get('correct_answers', 0)
    accuracy = data.get('accuracy', 0)
    points_earned = data.get('points_earned', 0)
    time_taken = data.get('time_taken', 0)
    quiz_data = json.dumps(data.get('quiz_data', {}))
    
    try:
        if accuracy >= 70:  
            execute_query('''
                UPDATE users SET 
                total_points = total_points + ?,
                quiz_streak = quiz_streak + 1,
                last_quiz_date = DATE('now')
                WHERE id = ?
            ''', (points_earned, session['user_id']))
        else:
            execute_query('''
                UPDATE users SET 
                total_points = total_points + ?,
                quiz_streak = 0,
                last_quiz_date = DATE('now')
                WHERE id = ?
            ''', (points_earned, session['user_id']))
        
        execute_insert('''
            INSERT INTO quiz_analytics 
            (user_id, total_questions, correct_answers, accuracy, time_taken, questions_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], questions_answered, correct_answers, accuracy, time_taken, quiz_data))
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        print(f"Error updating quiz stats: {e}")
        return jsonify({'error': 'Failed to update quiz statistics'}), 500

@api_bp.route('/get_quiz_analytics')
@login_required
def get_quiz_analytics():
    try:
        total_quizzes = execute_single(
            'SELECT COUNT(*) FROM quiz_analytics WHERE user_id = ?', 
            (session['user_id'],)
        )[0]
        
        avg_accuracy_result = execute_single(
            'SELECT AVG(accuracy) FROM quiz_analytics WHERE user_id = ?', 
            (session['user_id'],)
        )
        avg_accuracy = round(avg_accuracy_result[0] or 0, 1)
        
        recent_scores_data = execute_query('''
            SELECT accuracy FROM quiz_analytics WHERE user_id = ? 
            ORDER BY quiz_date DESC LIMIT 10
        ''', (session['user_id'],))
        recent_scores = [round(row[0]) for row in recent_scores_data]
        recent_scores.reverse()  
     
        improvement_rate = 0
        if len(recent_scores) >= 6:
            first_three = sum(recent_scores[:3]) / 3
            last_three = sum(recent_scores[-3:]) / 3
            improvement_rate = round(((last_three - first_three) / first_three) * 100, 1)
        
        best_category = 'Business Basics'  
        
        return jsonify({
            'total_quizzes': total_quizzes,
            'avg_accuracy': avg_accuracy,
            'recent_scores': recent_scores,
            'improvement_rate': max(0, improvement_rate),
            'best_category': best_category
        })
        
    except Exception as e:
        print(f"Error getting quiz analytics: {e}")
        return jsonify({
            'total_quizzes': 0,
            'avg_accuracy': 0,
            'recent_scores': [],
            'improvement_rate': 0,
            'best_category': 'Business Basics'
        }), 500

@api_bp.route('/delete_idea/<int:idea_id>', methods=['DELETE'])
@login_required
def delete_idea(idea_id):
    result = execute_single('SELECT user_id FROM ideas WHERE id = ?', (idea_id,))
    
    if not result:
        return jsonify({'error': 'Idea not found'}), 404
    
    if result[0] != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        execute_query('DELETE FROM idea_likes WHERE idea_id = ?', (idea_id,))
        execute_query('DELETE FROM comments WHERE idea_id = ?', (idea_id,))
        execute_query('DELETE FROM team_applications WHERE idea_id = ?', (idea_id,))
        execute_query('DELETE FROM teams WHERE idea_id = ?', (idea_id,))
        execute_query('DELETE FROM ideas WHERE id = ?', (idea_id,))
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error deleting idea: {e}")
        return jsonify({'error': 'Failed to delete idea'}), 500




@api_bp.route('/evaluate_idea/<int:idea_id>', methods=['POST'])
@login_required
def evaluate_idea(idea_id):
    print(f"Starting evaluation for idea ID: {idea_id}")
    
    result = execute_single('SELECT user_id FROM ideas WHERE id = ?', (idea_id,))
    
    if not result:
        print(f"Idea {idea_id} not found")
        return jsonify({'error': 'Idea not found'}), 404
    

    if result[0] != session['user_id']:
        print(f"User {session['user_id']} unauthorized to evaluate idea {idea_id}")
        return jsonify({'error': 'Unauthorized - You can only evaluate your own ideas'}), 403
    
    try:
        idea_data = execute_single('''
            SELECT title, problem_statement, solution_description, category, 
                   development_stage, target_market, budget_range, timeline, tags
            FROM ideas WHERE id = ?
        ''', (idea_id,))
        
        if not idea_data:
            print(f"Idea data not found for ID: {idea_id}")
            return jsonify({'error': 'Idea data not found'}), 404
        
        print(f"Retrieved idea data: {idea_data[0]}")  
        

        idea_dict = {
            'title': idea_data[0] or 'Untitled',
            'problem_statement': idea_data[1] or 'No problem statement provided',
            'solution_description': idea_data[2] or 'No solution description provided',
            'category': idea_data[3] or 'General',
            'development_stage': idea_data[4] or 'Idea',
            'target_market': idea_data[5] or 'Not specified',
            'budget_range': idea_data[6] or 'Not specified',
            'timeline': idea_data[7] or 'Not specified',
            'tags': idea_data[8] or ''
        }
        
        print(f"Prepared idea dict for evaluation: {idea_dict['title']}")
        
        try:
            from ai_evaluator import get_evaluator
            evaluator = get_evaluator()  
            print(f"Got evaluator: {type(evaluator).__name__}")
            
            evaluation = evaluator.evaluate_idea(idea_dict)
            print(f"Evaluation completed with rating: {evaluation.get('overall_rating', 'Unknown')}")
            
            try:
                evaluation_json = json.dumps(evaluation)
                execute_insert('''
                    INSERT OR REPLACE INTO idea_evaluations 
                    (idea_id, user_id, evaluation_data, created_date) 
                    VALUES (?, ?, ?, ?)
                ''', (idea_id, session['user_id'], evaluation_json, datetime.now().isoformat()))
                print(f"Saved evaluation to database for idea {idea_id}")
            except Exception as save_error:
                print(f"Warning: Failed to save evaluation to database: {save_error}")
            
            return jsonify({
                'success': True,
                'evaluation': evaluation,
                'message': 'Evaluation completed successfully'
            })
            
        except ImportError as import_error:
            print(f"Failed to import evaluator: {import_error}")
            return jsonify({
                'error': 'Evaluation service not available',
                'message': 'AI evaluator module could not be loaded'
            }), 500
            
    except Exception as e:
        print(f"Error evaluating idea {idea_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to evaluate idea', 
            'message': str(e)
        }), 500

@api_bp.route('/save_evaluation', methods=['POST'])
@login_required
def save_evaluation():
    data = request.get_json()
    idea_id = data.get('idea_id')
    evaluation_data = json.dumps(data.get('evaluation'))
    
    if not idea_id or not evaluation_data:
        return jsonify({'error': 'Idea ID and evaluation data are required'}), 400
    
    try:
        execute_insert('''
            INSERT OR REPLACE INTO idea_evaluations 
            (idea_id, user_id, evaluation_data) VALUES (?, ?, ?)
        ''', (idea_id, session['user_id'], evaluation_data))
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error saving evaluation: {e}")
        return jsonify({'error': 'Failed to save evaluation'}), 500