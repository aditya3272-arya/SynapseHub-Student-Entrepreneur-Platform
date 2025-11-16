import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
import uuid

def send_team_application_email(founder_email, founder_name, idea_title, applicant_name, message, skills):
    try:
        msg = MIMEMultipart()
        msg['From'] = Config.MAIL_USERNAME
        msg['To'] = founder_email
        msg['Subject'] = f"New Team Application for '{idea_title}'"
        
        base_url = "http://localhost:5000"  
        approve_url = f"{base_url}/approve_application/{idea_title.replace(' ', '_')}_{applicant_name}"
        
        body = f"""
Dear {founder_name},

You have received a new team application for your idea '{idea_title}'.

APPLICANT DETAILS:
• Name: {applicant_name}
• Skills: {skills}
• Message: {message}

NEXT STEPS:
To approve this application, click here: {approve_url}

To view and manage all applications, visit: {base_url}/teams

Best regards,
The SynapseHub Team

---
This is an automated message from SynapseHub - The Youth Entrepreneurship Platform
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
        server.starttls()
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"Team application email sent to {founder_email}")
        
    except Exception as e:
        print(f"Failed to send team application email: {e}")

def send_booking_confirmation_email(student_email, student_name, mentor_name, 
                                  session_date, session_time, session_topic, meeting_link):
    try:
        msg = MIMEMultipart()
        msg['From'] = Config.MAIL_USERNAME
        msg['To'] = student_email
        msg['Subject'] = f"Session Confirmed with {mentor_name} - SynapseHub"
        
        body = f"""
Dear {student_name},

Your mentorship session has been successfully booked!

SESSION DETAILS:
• Mentor: {mentor_name}
• Date: {session_date}
• Time: {session_time}
• Topic: {session_topic or 'General mentorship discussion'}
• Duration: 30 minutes

MEETING DETAILS:
Join your session using this link: {meeting_link}

IMPORTANT NOTES:
• Please join the meeting 5 minutes early
• Test your camera and microphone beforehand
• Prepare specific questions you'd like to discuss
• This session is completely free

NEED TO RESCHEDULE?
If you need to reschedule or cancel, please contact us at least 24 hours in advance.

We're excited to see you learn and grow!

Best regards,
The SynapseHub Team

---
SynapseHub - Empowering Young Entrepreneurs
Need help? Contact us at {Config.MAIL_USERNAME}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
        server.starttls()
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(Config.MAIL_USERNAME, student_email, text)
        server.quit()
        
        print(f"Confirmation email sent to {student_email}")
        
    except Exception as e:
        print(f"Failed to send booking confirmation email: {e}")

def send_welcome_email(user_email, username):
    try:
        msg = MIMEMultipart()
        msg['From'] = Config.MAIL_USERNAME
        msg['To'] = user_email
        msg['Subject'] = "Welcome to SynapseHub - Let's Build Something Amazing!"
        
        body = f"""
Dear {username},

Welcome to SynapseHub - the premier platform for young entrepreneurs!

We're thrilled to have you join our community of innovative minds who are passionate about creating solutions that matter.

GET STARTED:
• Submit your first business idea
• Take our daily entrepreneurship quiz
• Connect with mentors and fellow entrepreneurs
• Join collaborative teams
• Track your progress and achievements

WHAT'S NEXT?
1. Complete your profile to connect with like-minded peers
2. Browse existing ideas for inspiration
3. Submit your own innovative business concept
4. Start your entrepreneurship learning journey

NEED HELP?
• Visit our Help Center: /helpcenter
• Check out Safety Guidelines: /safety
• Review Terms & Privacy: /terms

We can't wait to see what amazing ideas you'll bring to life!

Best regards,
The SynapseHub Team

---
SynapseHub - Where Young Minds Build the Future
Follow us for daily entrepreneurship tips and success stories!
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
        server.starttls()
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"Welcome email sent to {user_email}")
        
    except Exception as e:
        print(f"Failed to send welcome email: {e}")

def send_password_reset_email(user_email, username, reset_token):
    try:
        msg = MIMEMultipart()
        msg['From'] = Config.MAIL_USERNAME
        msg['To'] = user_email
        msg['Subject'] = "Reset Your SynapseHub Password"
        
        base_url = "http://localhost:5000"  
        reset_url = f"{base_url}/reset_password/{reset_token}"
        
        body = f"""
Dear {username},

We received a request to reset your SynapseHub password.

To reset your password, click the link below:
{reset_url}

This link will expire in 1 hour for security reasons.

If you didn't request this password reset, please ignore this email - your account is secure.

Best regards,
The SynapseHub Team

---
SynapseHub - Secure & Trusted Platform for Young Entrepreneurs
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
        server.starttls()
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"Password reset email sent to {user_email}")
        
    except Exception as e:
        print(f"Failed to send password reset email: {e}")

def generate_meeting_link():
    meeting_id = str(uuid.uuid4())[:8]
    return f"https://meet.google.com/{meeting_id}"