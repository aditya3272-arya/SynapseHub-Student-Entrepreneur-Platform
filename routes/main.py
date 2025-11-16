from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from routes.auth import login_required
from database import execute_query, execute_single, execute_insert
import random


main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_ideas_count = execute_single(
        'SELECT COUNT(*) FROM ideas WHERE user_id = ?', 
        (session['user_id'],)
    )[0]
    
    recent_ideas = execute_query('''
        SELECT i.title, i.created_date, u.username 
        FROM ideas i JOIN users u ON i.user_id = u.id 
        ORDER BY i.created_date DESC LIMIT 5
    ''')
    
    user_stats = execute_single(
        'SELECT quiz_streak, total_points FROM users WHERE id = ?', 
        (session['user_id'],)
    )
    
    avg_accuracy_result = execute_single(
        'SELECT AVG(accuracy) FROM quiz_analytics WHERE user_id = ?', 
        (session['user_id'],)
    )
    avg_accuracy = avg_accuracy_result[0] if avg_accuracy_result[0] else 0
    
    enhanced_stats = list(user_stats) + [round(avg_accuracy, 1)] if user_stats else [0, 0, 0]
    
    return render_template('dashboard.html', 
                         user_ideas_count=user_ideas_count,
                         recent_ideas=recent_ideas,
                         user_stats=enhanced_stats)

@main_bp.route('/ideas')
@login_required
def ideas():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    sort_by = request.args.get('sort', 'newest')
    
    query = '''SELECT 
                    i.id,
                    COALESCE(i.title, '') as title,
                    COALESCE(i.problem_statement, '') as problem_statement,
                    COALESCE(i.solution_description, '') as solution_description,
                    COALESCE(i.category, 'General') as category,
                    COALESCE(DATE(i.created_date), DATE('now')) as created_date,
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
               WHERE COALESCE(i.status, 'active') = 'active' '''
    params = []
    
    if search:
        query += ''' AND (COALESCE(i.title, '') LIKE ? 
                     OR COALESCE(i.problem_statement, '') LIKE ? 
                     OR COALESCE(i.solution_description, '') LIKE ? 
                     OR COALESCE(i.tags, '') LIKE ?)'''
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param, search_param])
    
    if category:
        query += ' AND COALESCE(i.category, \'\') = ?'
        params.append(category)
    
    if sort_by == 'popular':
        query += ' ORDER BY COALESCE(i.like_count, 0) DESC, COALESCE(i.view_count, 0) DESC, i.created_date DESC'
    elif sort_by == 'views':
        query += ' ORDER BY COALESCE(i.view_count, 0) DESC, i.created_date DESC'
    elif sort_by == 'comments':
        query += ' ORDER BY COALESCE(i.comment_count, 0) DESC, i.created_date DESC'
    else:
        query += ' ORDER BY i.created_date DESC'
    
    try:
        all_ideas = execute_query(query, params)
        print(f"Database query executed successfully. Loaded {len(all_ideas)} ideas")
        
        validated_ideas = []
        for idx, idea in enumerate(all_ideas):
            if len(idea) >= 18:
                validated_idea = list(idea)
                
                validated_idea[6] = validated_idea[6] if validated_idea[6] is not None else 0  
                validated_idea[7] = validated_idea[7] if validated_idea[7] is not None else 0
                validated_idea[14] = validated_idea[14] if validated_idea[14] is not None else 0  
                validated_idea[17] = validated_idea[17] if validated_idea[17] is not None else 0  
                
                validated_ideas.append(tuple(validated_idea))
            else:
                print(f"Warning: Idea {idea[0] if idea else 'Unknown'} has only {len(idea)} columns, expected 18. Skipping.")
                
        print(f"Validated {len(validated_ideas)} ideas for display")
                
    except Exception as e:
        print(f"Database error in ideas route: {e}")
        import traceback
        traceback.print_exc()
        validated_ideas = []
        flash('Error loading ideas. Please try again.', 'error')
    
    try:
        categories_result = execute_query(
            'SELECT DISTINCT category FROM ideas WHERE category IS NOT NULL AND category != "" AND category != "null" ORDER BY category'
        )
        categories = [row[0] for row in categories_result if row[0]]
    except Exception as e:
        print(f"Error fetching categories: {e}")
        categories = []
    
    return render_template('ideas.html', 
                         ideas=validated_ideas, 
                         categories=categories,
                         current_search=search, 
                         current_category=category, 
                         current_sort=sort_by)

@main_bp.route('/idea/<int:idea_id>')
@login_required
def idea_detail(idea_id):
    try:
        idea_data = execute_single('''
            SELECT 
                i.id,
                COALESCE(i.title, '') as title,
                COALESCE(i.problem_statement, '') as problem_statement,
                COALESCE(i.solution_description, '') as solution_description,
                COALESCE(i.category, 'General') as category,
                COALESCE(i.created_date, '') as created_date,
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
            WHERE i.id = ? AND COALESCE(i.status, 'active') = 'active'
        ''', (idea_id,))
        
        if not idea_data:
            abort(404)
        
        idea = {
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
        }
        
        comments_data = execute_query('''
            SELECT 
                c.comment_text,
                c.created_date,
                u.username
            FROM comments c 
            JOIN users u ON c.user_id = u.id 
            WHERE c.idea_id = ? 
            ORDER BY c.created_date DESC
        ''', (idea_id,))
        
        comments = []
        for comment_row in comments_data:
            comments.append({
                'comment_text': comment_row[0],
                'created_date': comment_row[1],
                'username': comment_row[2]
            })
        
        return render_template('idea_detail.html', idea=idea, comments=comments)
        
    except Exception as e:
        print(f"Error loading idea detail: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading idea details. Please try again.', 'error')
        return redirect(url_for('main.ideas'))

@main_bp.route('/submit_idea', methods=['GET', 'POST'])
@login_required
def submit_idea():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        problem = request.form.get('problem_statement', '').strip()
        solution = request.form.get('solution_description', '').strip()
        category = request.form.get('category', '').strip()
        
        if not all([title, problem, solution, category]):
            flash('Please fill in all required fields (Title, Problem Statement, Solution Description, and Category)')
            return redirect(url_for('main.submit_idea'))
        
        development_stage = request.form.get('development_stage', 'Idea')
        target_market = request.form.get('target_market', '')
        budget_range = request.form.get('budget_range', '')
        timeline = request.form.get('timeline', '')
        tags = request.form.get('tags', '')
        team_needs = request.form.get('team_needs', '')
        inspiration = request.form.get('inspiration', '')
        open_collaboration = 1 if request.form.get('open_collaboration') else 0
        
        try:
            from database import execute_insert
            from datetime import datetime
            
            idea_id = execute_insert('''
                INSERT INTO ideas (
                    user_id, title, problem_statement, solution_description, 
                    category, development_stage, target_market, budget_range, 
                    timeline, tags, team_needs, inspiration, open_collaboration,
                    view_count, like_count, comment_count, status, created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'], title, problem, solution, category,
                development_stage, target_market, budget_range, timeline,
                tags, team_needs, inspiration, open_collaboration,
                0, 0, 0, 'active', datetime.now().isoformat()
            ))
            
            print(f"Successfully inserted new idea with ID: {idea_id}")
            
            if open_collaboration and idea_id:
                try:
                    team_id = random.randint(1000, 9999)
                    execute_insert('''
                        INSERT INTO teams (team_id, idea_id, member_username, is_founder, status)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (team_id, idea_id, session['username'], 1, 'active'))
                    print(f"Created team {team_id} for idea {idea_id}")
                except Exception as team_error:
                    print(f"Warning: Failed to create team for idea {idea_id}: {team_error}")
            
            flash('Your idea has been submitted successfully!', 'success')
            return redirect(url_for('main.ideas'))
            
        except Exception as e:
            print(f"Error submitting idea: {e}")
            import traceback
            traceback.print_exc()
            flash('Error submitting idea. Please try again.', 'error')
            return redirect(url_for('main.submit_idea'))
    
    return render_template('submit_idea.html')

@main_bp.route('/mentors')
@login_required
def mentors():
    try:
        mentors_data = execute_query('SELECT * FROM mentors ORDER BY rating DESC')
        return render_template('mentors.html', mentors=mentors_data)
    except Exception as e:
        print(f"Error fetching mentors: {e}")
        flash('Error loading mentors. Please try again.')
        return render_template('mentors.html', mentors=[])

@main_bp.route('/teams')
@login_required
def teams():
    username = session['username']
    
    my_teams = []
    teams_data = execute_query('''
        SELECT DISTINCT i.id, i.title, i.category, i.problem_statement, t.team_id, i.user_id
        FROM ideas i 
        JOIN teams t ON i.id = t.idea_id 
        JOIN users u ON i.user_id = u.id
        WHERE t.member_username = ? AND t.status = 'active'
    ''', (username,))
    
    for row in teams_data:
        members_data = execute_query('''
            SELECT member_username, is_founder FROM teams 
            WHERE team_id = ? AND status = 'active'
        ''', (row[4],))
        members = [{'username': m[0], 'is_founder': bool(m[1])} for m in members_data]
        
        author_result = execute_single('SELECT username FROM users WHERE id = ?', (row[5],))
        author_username = author_result[0] if author_result else 'Unknown'
        
        my_teams.append({
            'team_id': row[4],
            'idea_title': row[1],
            'category': row[2],
            'description': row[3],
            'members': members,
            'is_member_founder': author_username == username
        })
    
    collaborative_ideas_data = execute_query('''
        SELECT i.id, i.title, i.problem_statement, i.solution_description, i.category, u.username, i.team_needs 
        FROM ideas i 
        JOIN users u ON i.user_id = u.id
        WHERE i.open_collaboration = 1 AND u.username != ?
        ORDER BY i.created_date DESC
    ''', (username,))
    
    collaborative_ideas = [
        {
            'id': r[0], 'title': r[1], 'problem': r[2], 'solution': r[3], 
            'category': r[4], 'author': r[5], 'team_needs': r[6]
        } 
        for r in collaborative_ideas_data
    ]
    
    applications_data = execute_query('''
        SELECT ta.idea_id, i.title, u.username, ta.message, ta.status, ta.applied_date
        FROM team_applications ta
        JOIN ideas i ON ta.idea_id = i.id
        JOIN users u ON i.user_id = u.id
        WHERE ta.applicant_username = ?
        ORDER BY ta.applied_date DESC
    ''', (username,))
    
    my_applications = [
        {
            'idea_id': r[0], 'idea_title': r[1], 'idea_author': r[2], 
            'message': r[3], 'status': r[4], 'applied_date': r[5]
        } 
        for r in applications_data
    ]
    
    return render_template('teams.html', 
                         my_teams=my_teams,
                         collaborative_ideas=collaborative_ideas,
                         my_applications=my_applications)

@main_bp.route('/quiz')
@login_required
def quiz():
    try:
        user_data = execute_single(
            'SELECT quiz_streak, total_points FROM users WHERE id = ?', 
            (session['user_id'],)
        )
        
        avg_accuracy_result = execute_single(
            'SELECT AVG(accuracy) FROM quiz_analytics WHERE user_id = ?', 
            (session['user_id'],)
        )
        avg_accuracy = round(avg_accuracy_result[0] or 0, 1)
        
        user_stats = [user_data[0], user_data[1], avg_accuracy] if user_data else [0, 0, 0]
        
        return render_template('quiz.html', user_stats=user_stats)
        
    except Exception as e:
        print(f"Error loading quiz page: {e}")
        return render_template('quiz.html', user_stats=[0, 0, 0])

@main_bp.route('/profile')
@login_required
def profile():
    try:
        user = execute_single('SELECT * FROM users WHERE id = ?', (session['user_id'],))
        
        user_ideas = execute_query(
            'SELECT * FROM ideas WHERE user_id = ? ORDER BY created_date DESC', 
            (session['user_id'],)
        )
        
        user_teams_query = '''
            SELECT i.title, t.team_id, COUNT(*) as member_count,
                   CASE WHEN i.user_id = ? THEN 'Founder' ELSE 'Member' END as role
            FROM teams t 
            JOIN ideas i ON t.idea_id = i.id 
            WHERE t.member_username = ? AND COALESCE(t.status, 'active') = 'active'
            GROUP BY t.team_id
        '''
        user_teams_data = execute_query(user_teams_query, (session['user_id'], session['username']))
        user_teams = [{'idea_title': r[0], 'team_id': r[1], 'member_count': r[2], 'role': r[3]} 
                      for r in user_teams_data]
        
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
        
        improvement_rate = 0
        if len(recent_scores) >= 6:
            first_three = sum(recent_scores[-3:]) / 3
            last_three = sum(recent_scores[:3]) / 3
            improvement_rate = round(((last_three - first_three) / first_three) * 100, 1) if first_three > 0 else 0
        
        quiz_stats = {
            'total_quizzes': total_quizzes,
            'avg_accuracy': avg_accuracy,
            'best_category': 'Business Basics',  
            'improvement_rate': max(0, improvement_rate)
        }
        
        return render_template('profile.html', 
                             user=user, 
                             user_ideas=user_ideas,
                             user_teams=user_teams,
                             teams_joined=len(user_teams),
                             quiz_stats=quiz_stats)
                             
    except Exception as e:
        print(f"Error loading profile: {e}")
        flash('Error loading profile. Please try again.')
        return redirect(url_for('main.dashboard'))

@main_bp.route("/helpcenter")
def helpcenter():
    return render_template("helpcenter.html")

@main_bp.route("/safety")
def safety():
    return render_template("safety.html") 

@main_bp.route("/pp")
def privacy_policy():
    return render_template("pp.html")

@main_bp.route("/terms")
def terms():
    return render_template("terms.html")