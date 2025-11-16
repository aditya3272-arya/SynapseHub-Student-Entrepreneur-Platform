from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import execute_single, execute_insert

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def landing():
    return render_template('landing.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        age = request.form.get('age', 16)
        
        
        if not username or not email or not password:
            flash('All fields are required')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long')
            return redirect(url_for('auth.register'))
        
        
        existing_user = execute_single(
            'SELECT id FROM users WHERE email = ? OR username = ?', 
            (email, username)
        )
        
        if existing_user:
            flash('Username or email already exists')
            return redirect(url_for('auth.register'))
        
        
        password_hash = generate_password_hash(password)
        try:
            user_id = execute_insert(
                '''INSERT INTO users (username, email, password_hash, age) 
                   VALUES (?, ?, ?, ?)''', 
                (username, email, password_hash, age)
            )
            
            
            session['user_id'] = user_id
            session['username'] = username
            
            flash('Registration successful! Welcome to SynapseHub!')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            flash('Registration failed. Please try again.')
            return redirect(url_for('auth.register'))
    
    return render_template('landing.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    
    if not email or not password:
        flash('Email and password are required')
        return redirect(url_for('auth.landing'))
    
    
    user = execute_single(
        'SELECT id, username, password_hash FROM users WHERE email = ?', 
        (email,)
    )
    
    if user and check_password_hash(user[2], password):
        session['user_id'] = user[0]
        session['username'] = user[1]
        flash(f'Welcome back, {user[1]}!')
        return redirect(url_for('main.dashboard'))
    
    flash('Invalid email or password')
    return redirect(url_for('auth.landing'))

@auth_bp.route('/logout')
def logout():
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}! You have been logged out.')
    return redirect(url_for('auth.landing'))

def login_required(f):
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page')
            return redirect(url_for('auth.landing'))
        return f(*args, **kwargs)
    return decorated_function