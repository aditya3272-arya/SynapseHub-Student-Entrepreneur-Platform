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


def generate_meeting_link():
    meeting_id = str(uuid.uuid4())[:8]
    return f"https://meet.google.com/{meeting_id}"