import sqlite3
import json
from werkzeug.security import generate_password_hash
from datetime import datetime

def get_db_connection():
    from config import Config
    conn = sqlite3.connect(Config.DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect('synapsehub.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        age INTEGER,
        skills TEXT,
        interests TEXT,
        bio TEXT,
        profile_image TEXT DEFAULT 'default-avatar.png',
        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        quiz_streak INTEGER DEFAULT 0,
        total_points INTEGER DEFAULT 0,
        last_quiz_date DATE
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS ideas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT NOT NULL,
        problem_statement TEXT NOT NULL,
        solution_description TEXT NOT NULL,
        category TEXT,
        status TEXT DEFAULT 'active',
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        view_count INTEGER DEFAULT 0,
        like_count INTEGER DEFAULT 0,
        development_stage TEXT DEFAULT "Idea",
        target_market TEXT DEFAULT "",
        budget_range TEXT DEFAULT "",
        timeline TEXT DEFAULT "",
        tags TEXT DEFAULT "",
        team_needs TEXT DEFAULT "",
        inspiration TEXT DEFAULT "",
        open_collaboration INTEGER DEFAULT 0,
        comment_count INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        idea_id INTEGER,
        user_id INTEGER,
        comment_text TEXT NOT NULL,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (idea_id) REFERENCES ideas (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS session_bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        mentor_id INTEGER,
        student_name TEXT NOT NULL,
        student_email TEXT NOT NULL,
        session_date DATE NOT NULL,
        session_time TEXT NOT NULL,
        session_topic TEXT,
        meeting_link TEXT,
        status TEXT DEFAULT 'confirmed',
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (mentor_id) REFERENCES mentors (id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER,
        idea_id INTEGER,
        member_username TEXT,
        is_founder INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active',
        joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (idea_id) REFERENCES ideas (id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS team_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        idea_id INTEGER,
        applicant_username TEXT,
        message TEXT,
        skills TEXT,
        experience TEXT,
        availability TEXT,
        status TEXT DEFAULT 'pending',
        applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (idea_id) REFERENCES ideas (id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS team_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER,
        username TEXT,
        message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS mentors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        expertise TEXT,
        bio TEXT,
        availability TEXT,
        rating REAL DEFAULT 5.0,
        verified_status INTEGER DEFAULT 1,
        profile_image TEXT DEFAULT 'mentor-default.png',
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS quiz_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        options TEXT NOT NULL,
        correct_answer INTEGER NOT NULL,
        explanation TEXT,
        category TEXT,
        difficulty_level INTEGER DEFAULT 1
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS user_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        quiz_answers TEXT,
        correct_count INTEGER DEFAULT 0,
        streak_count INTEGER DEFAULT 0,
        achievement_badges TEXT,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS idea_likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        idea_id INTEGER,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (idea_id) REFERENCES ideas (id),
        UNIQUE(user_id, idea_id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS quiz_analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        quiz_date DATE DEFAULT CURRENT_DATE,
        total_questions INTEGER,
        correct_answers INTEGER,
        accuracy REAL,
        time_taken INTEGER,
        questions_data TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS profile_updates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        field_updated TEXT,
        old_value TEXT,
        new_value TEXT,
        updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS idea_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        idea_id INTEGER,
        user_id INTEGER,
        evaluation_data TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (idea_id) REFERENCES ideas (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()

def populate_sample_data():
    conn = sqlite3.connect('synapsehub.db')
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM ideas')
    if c.fetchone()[0] > 0:
        conn.close()
        return
    
    sample_users = [
        ('alex_teen', 'alex@example.com', generate_password_hash('password123'), 16, 'Programming, Design', 'Technology, Gaming', 'Passionate about creating apps that solve real problems'),
        ('emma_innovates', 'emma@example.com', generate_password_hash('password123'), 15, 'Marketing, Writing', 'Social Impact, Environment', 'Love building solutions that make the world better'),
        ('dev_sam', 'sam@example.com', generate_password_hash('password123'), 17, 'Coding, Analytics', 'AI, Data Science', 'Fascinated by how technology can transform education')
    ]
    
    for user in sample_users:
        try:
            c.execute('INSERT INTO users (username, email, password_hash, age, skills, interests, bio) VALUES (?, ?, ?, ?, ?, ?, ?)', user)
        except sqlite3.IntegrityError:
            pass
    
    sample_ideas = [
        (1, 'EcoTrack - Carbon Footprint App', 'Students want to be environmentally conscious but don\'t know where to start or how to track their impact', 'A mobile app that gamifies carbon footprint tracking for teens, with challenges, rewards, and community features to make sustainability fun and social', 'Environment', 'Prototype', 'Students aged 13-18', '$5,000 - $15,000', '3-6 months', 'sustainability,environment,mobile app,gamification', 'Looking for developers and marketers', 'Inspired by seeing waste in my school cafeteria', 1, 15, 8, 3),
        (2, 'StudyBuddy - AI Homework Helper', 'Students struggle with homework when parents can\'t help and tutoring is expensive', 'An AI-powered study companion that provides personalized help, explains concepts step-by-step, and connects students with peer tutors', 'Education', 'MVP', 'High school students', '$10,000 - $25,000', '6-12 months', 'AI,education,tutoring,machine learning', 'Need AI/ML specialists and UX designers', 'Personal struggles with math homework', 1, 22, 12, 5),
        (3, 'LocalTeen - Community Service Platform', 'Teenagers want to volunteer but don\'t know where to find opportunities that match their interests and schedule', 'A platform connecting teens with local volunteer opportunities, tracking service hours, and building portfolios for college applications', 'Social Impact', 'Idea', 'Teens seeking volunteer opportunities', '$3,000 - $8,000', '2-4 months', 'volunteering,community service,social impact', 'Seeking web developers and community outreach specialists', 'Difficulty finding volunteer opportunities myself', 0, 18, 6, 2),
        (1, 'FoodSaver - Restaurant Waste Reducer', 'Restaurants throw away tons of food daily while many students struggle to afford meals', 'An app connecting students with restaurants to purchase surplus food at discounted prices before closing time', 'Food & Sustainability', 'Research', 'College students and restaurants', '$8,000 - $20,000', '4-8 months', 'food waste,sustainability,mobile app,marketplace', 'Looking for business development and app developers', 'Seeing food waste at local restaurants', 1, 25, 15, 7),
        (3, 'SkillSwap Academy', 'Students have unique talents but no platform to teach others and earn money from their skills', 'A peer-to-peer learning platform where students can teach and learn from each other, from music to coding to sports', 'Education', 'Beta', 'Students with teachable skills', '$15,000 - $30,000', '6-10 months', 'peer learning,skills,education,marketplace', 'Need platform developers and marketing experts', 'Wanting to monetize my guitar skills', 0, 30, 20, 9),
        (2, 'MindfulTeen - Mental Health Support', 'Teenagers face increasing mental health challenges but traditional therapy is stigmatized and expensive', 'An anonymous peer support platform with guided meditation, mood tracking, and trained teen counselors', 'Health & Wellness', 'Concept', 'Teenagers facing mental health challenges', '$12,000 - $25,000', '8-12 months', 'mental health,peer support,wellness,meditation', 'Seeking psychology students and app developers', 'Personal experience with teen mental health issues', 1, 35, 25, 12)
    ]
    
    for idea in sample_ideas:
        c.execute('''INSERT INTO ideas (user_id, title, problem_statement, solution_description, category, 
                     development_stage, target_market, budget_range, timeline, tags, team_needs, inspiration, 
                     open_collaboration, view_count, like_count, comment_count) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', idea)
    
    sample_mentors = [
        ('Sarah Chen', 'Tech Entrepreneurship, Product Development', 
         'Former startup founder who built and sold a successful EdTech company. Now mentoring the next generation of teen entrepreneurs with focus on product-market fit and scaling strategies.', 
         'Weekdays 6-8pm IST, Weekends 10am-2pm IST', 4.9),
        ('Dr. Priya Patel', 'Business Strategy, Finance', 
         'MBA professor and angel investor specializing in youth entrepreneurship and sustainable business models. Expert in financial planning and fundraising strategies.', 
         'Weekends 2-5pm IST, Wednesdays 8-10pm IST', 4.9),
        ('Lisa Wang', 'Social Impact, Non-Profit Strategy', 
         'Social entrepreneur who has launched multiple successful non-profit initiatives focused on youth empowerment. Expert in impact measurement and sustainable social ventures.', 
         'Flexible scheduling - contact for availability', 5.0),
        ('David Kumar', 'E-commerce, Retail Strategy', 
         'Built and scaled multiple e-commerce businesses from startup to multi-million dollar revenue. Specializes in online marketplace strategies and customer acquisition.', 
         'Monday/Wednesday/Friday 7-9pm IST', 4.6),
        ('Rachel Foster', 'Content Creation, Personal Branding', 
         'Content strategist and personal branding expert who has helped 100+ young entrepreneurs build their online presence and thought leadership.', 
         'Tuesday/Thursday 6-8pm IST, Saturday 11am-1pm IST', 4.8)
    ]
    
    for mentor in sample_mentors:
        c.execute('INSERT INTO mentors (name, expertise, bio, availability, rating) VALUES (?, ?, ?, ?, ?)', mentor)
    
    sample_questions = [
        ('What is the most important first step when starting a business?', '["Get funding", "Validate your idea with customers", "Build a perfect product", "Create a business plan"]', 1, 'Understanding if people actually want your solution is crucial before investing time and money', 'Business Basics', 1),
        ('What does MVP stand for in startup terminology?', '["Most Valuable Player", "Minimum Viable Product", "Maximum Value Proposition", "Main Vision Plan"]', 1, 'MVP means building the simplest version of your product to test with real customers', 'Product Development', 1),
        ('Which quality is most important for young entrepreneurs?', '["Having lots of money", "Being the smartest person", "Persistence and resilience", "Having famous connections"]', 2, 'Success comes from not giving up when facing challenges and learning from failures', 'Entrepreneurship', 1),
        ('What is the best way to find your first customers?', '["Expensive advertising", "Talk to people who have the problem", "Wait for them to find you", "Copy what competitors do"]', 1, 'Direct customer conversations help you understand needs and build relationships', 'Marketing', 1),
        ('Why do most startups fail?', '["Not enough funding", "Bad technology", "No market need for the product", "Too much competition"]', 2, 'Building something people don\'t actually want is the #1 reason startups fail', 'Business Strategy', 1),
        ('What is bootstrapping in business?', '["Using free software", "Starting with your own money", "Copying successful businesses", "Working from home"]', 1, 'Bootstrapping means funding your startup with personal savings rather than external investment', 'Finance', 1),
        ('What does B2B mean?', '["Back to Business", "Business to Business", "Buy to Build", "Best Business Basics"]', 1, 'B2B refers to businesses that sell products or services to other businesses', 'Business Terms', 1),
        ('What is a business model?', '["A plan for making money", "A template for websites", "A type of contract", "A marketing strategy"]', 0, 'A business model describes how a company creates, delivers, and captures value', 'Business Strategy', 1),
        ('What is the purpose of market research?', '["To waste time", "To understand your customers and competition", "To impress investors", "To delay product launch"]', 1, 'Market research helps you understand customer needs and market opportunities', 'Market Research', 1),
        ('What is a target audience?', '["Everyone in the world", "People who might buy your product", "Your competitors", "Your employees"]', 1, 'A target audience is the specific group of people most likely to buy your product', 'Marketing', 1),
        ('What does ROI stand for?', '["Return on Investment", "Rate of Interest", "Risk of Investment", "Reason of Investment"]', 0, 'ROI measures how much profit you make compared to how much you invested', 'Finance', 1),
        ('What is the main goal of a pitch presentation?', '["To show off", "To get funding or customers", "To confuse people", "To waste time"]', 1, 'A pitch should clearly communicate your value proposition to gain support', 'Presentation', 1)
    ]
    
    for question in sample_questions:
        c.execute('INSERT INTO quiz_questions (question, options, correct_answer, explanation, category, difficulty_level) VALUES (?, ?, ?, ?, ?, ?)', question)
    
    conn.commit()
    conn.close()

def update_database_schema():
    conn = sqlite3.connect('synapsehub.db')
    c = conn.cursor()
    
    def column_exists(table_name, column_name):
        c.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in c.fetchall()]
        return column_name in columns
    
    ideas_columns = [
        ('development_stage', 'TEXT DEFAULT "Idea"'),
        ('target_market', 'TEXT DEFAULT ""'),
        ('budget_range', 'TEXT DEFAULT ""'),
        ('timeline', 'TEXT DEFAULT ""'),
        ('tags', 'TEXT DEFAULT ""'),
        ('team_needs', 'TEXT DEFAULT ""'),
        ('inspiration', 'TEXT DEFAULT ""'),
        ('open_collaboration', 'INTEGER DEFAULT 0'),
        ('comment_count', 'INTEGER DEFAULT 0'),
        ('view_count', 'INTEGER DEFAULT 0'),
        ('like_count', 'INTEGER DEFAULT 0')
    ]
    
    for column_name, column_type in ideas_columns:
        if not column_exists('ideas', column_name):
            try:
                c.execute(f'ALTER TABLE ideas ADD COLUMN {column_name} {column_type}')
                print(f"Added column {column_name} to ideas table")
            except sqlite3.OperationalError as e:
                print(f"Could not add column {column_name}: {e}")
    
    c.execute('''UPDATE ideas SET 
                 view_count = COALESCE(view_count, 0),
                 like_count = COALESCE(like_count, 0),
                 comment_count = COALESCE(comment_count, 0),
                 development_stage = COALESCE(development_stage, "Idea"),
                 target_market = COALESCE(target_market, ""),
                 budget_range = COALESCE(budget_range, ""),
                 timeline = COALESCE(timeline, ""),
                 tags = COALESCE(tags, ""),
                 team_needs = COALESCE(team_needs, ""),
                 inspiration = COALESCE(inspiration, ""),
                 open_collaboration = COALESCE(open_collaboration, 0)
                 WHERE view_count IS NULL OR like_count IS NULL OR comment_count IS NULL
                 OR development_stage IS NULL OR open_collaboration IS NULL''')

    conn.commit()
    conn.close()

def execute_query(query, params=None):
    conn = get_db_connection()
    try:
        if params:
            result = conn.execute(query, params)
        else:
            result = conn.execute(query)
        data = result.fetchall()
        conn.commit()
        return data
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_single(query, params=None):
    conn = get_db_connection()
    try:
        if params:
            result = conn.execute(query, params)
        else:
            result = conn.execute(query)
        data = result.fetchone()
        conn.commit()
        return data
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_insert(query, params=None):
    conn = get_db_connection()
    try:
        cursor = conn.execute(query, params) if params else conn.execute(query)
        last_id = cursor.lastrowid
        conn.commit()
        return last_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()