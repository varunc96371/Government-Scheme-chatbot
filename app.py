import os
import time
import threading
import resend
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.db import init_db, register_user, validate_user, save_chat_message, get_chat_history, clear_chat_history, get_user_by_username, get_user_by_email, update_user_password, save_feedback, get_all_schemes, get_scheme_by_id
from models.recommender import generate_recommendation_response

# Load environment configurations
load_dotenv()

app = Flask(__name__)

# Basic Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'schemeai-dev-secret-key-12345')
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
app.config['DEBUG'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize SQLite database and seed initial schemes
with app.app_context():
    init_db()

# --- Email Helpers ---

def send_email(to_email, subject, body_text, from_email=None):
    """
    Sends an email using configured SMTP credentials.
    Tries SSL on port 465 first (fast & reliable on all networks).
    Includes automatic retry on transient handshake disconnection.
    """
    mail_username = os.environ.get('MAIL_USERNAME')
    mail_password = os.environ.get('MAIL_PASSWORD')

    if not mail_username or not mail_password:
        print("[Email Warning] MAIL_USERNAME or MAIL_PASSWORD not configured in .env")
        return False

    sender_display = from_email or os.environ.get('MAIL_FROM', 'jyothisreelakshmi129@gmail.com')

    msg = MIMEMultipart()
    msg['From'] = f"SchemeAI <{sender_display}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

    # Attempt 1: Port 465 (SSL) with automatic retry on transient socket reset
    for attempt in range(2):
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=12) as server:
                server.login(mail_username, mail_password)
                server.send_message(msg)
                print(f"[Email Success] Sent email to {to_email} via SSL:465")
                return True
        except Exception as ssl_err:
            if attempt == 0:
                print(f"[Email Retry] SSL:465 attempt 1 failed ({ssl_err}), retrying in 1s...")
                time.sleep(1.0)
            else:
                print(f"[Email Warning] SSL:465 failed after retry ({ssl_err}), trying port 587...")

    # Attempt 2: Port 587 (STARTTLS fallback)
    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=12) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)
            print(f"[Email Success] Sent email to {to_email} via STARTTLS:587")
            return True
    except Exception as tls_err:
        print(f"[Email Error] Failed to send email to {to_email}: {tls_err}")
        return False


def notify_feedback(name, email, message):
    """
    Dispatches:
    1. Notification email to the SchemeAI admin/team with feedback details.
    2. Confirmation receipt email to the citizen who submitted the feedback.
    """
    admin_email = os.environ.get('NOTIFICATION_EMAIL') or 'jyothisreelakshmi129@gmail.com'

    # 1. Admin notification email
    admin_subject = f"SchemeAI: New Feedback from {name}"
    admin_body = f"""Hello SchemeAI Team,

A citizen has submitted new feedback on the SchemeAI portal:

Name: {name}
Email: {email}

Message:
{message}

---
SchemeAI Notification Service
"""
    send_email(admin_email, admin_subject, admin_body)

    # 2. Citizen confirmation email
    if email and '@' in email and '.' in email:
        time.sleep(1.0)
        user_subject = "SchemeAI - Thank you for your feedback!"
        user_body = f"""Hello {name},

Thank you for reaching out to SchemeAI! We have successfully received your feedback:

"{message}"

Our team reviews every suggestion to continuously improve government scheme recommendations and access for citizens across India.

If you have any further questions or suggestions, feel free to visit our portal anytime.

Warm regards,
SchemeAI Team
Government Schemes Portal
"""
        send_email(email, user_subject, user_body)


def notify_feedback_async(name, email, message):
    """
    Dispatches feedback emails in a background thread so the user UI responds instantly.
    """
    thread = threading.Thread(
        target=notify_feedback,
        args=(name, email, message),
        daemon=True
    )
    thread.start()

@app.route('/')
def home():
    """
    Renders the homepage/landing portal for SchemeAI.
    """
    # Check if user is logged in to dynamically show dashboard options in navbar
    logged_in = 'user_id' in session
    username = session.get('username')
    return render_template('index.html', logged_in=logged_in, username=username)

# --- Authentication Routes ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user account registration.
    """
    if 'user_id' in session:
        return redirect(url_for('chat_workspace'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validations
        if not username or not email or not password:
            error = "All fields are required."
        elif len(username) < 3:
            error = "Username must be at least 3 characters long."
        elif len(password) < 6:
            error = "Password must be at least 6 characters long."
        else:
            # Register user
            success = register_user(username, email, password)
            if success:
                # Redirect to login page upon success
                return redirect(url_for('login', registered='success'))
            else:
                error = "Username is already taken. Please choose another."
                
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login authentication.
    """
    if 'user_id' in session:
        return redirect(url_for('chat_workspace'))

    error = None
    success_msg = None
    
    # Display registration success alert if navigated from register page
    if request.args.get('registered') == 'success':
        success_msg = "Account created successfully! Please log in."

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            error = "Please fill in all fields."
        else:
            # Validate credentials
            user = validate_user(username, password)
            if user:
                # Set session cookies
                session['user_id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('chat_workspace'))
            else:
                error = "Invalid username or password. Please try again."
                
    return render_template('login.html', error=error, success_msg=success_msg)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    default_email = request.args.get('email', '')
    if not default_email and 'username' in session:
        u = get_user_by_username(session['username'])
        if u and u['email']:
            default_email = u['email']

    if request.method == 'POST':
        input_val = request.form.get('email', '').strip()

        if not input_val:
            return render_template(
                'forgot_password.html',
                default_email=default_email,
                error='Please enter your registered email or username.'
            )

        # Allow lookup by registered email OR by username
        user = get_user_by_email(input_val) or get_user_by_username(input_val)

        if not user:
            return render_template(
                'forgot_password.html',
                default_email=input_val,
                error='No account found with this email or username.'
            )

        target_email = user['email'] if user['email'] else 'jyothisreelakshmi129@gmail.com'

        # Create a secure signed reset token
        token = serializer.dumps(user['id'], salt='password-reset')

        # Create reset link
        reset_link = url_for(
            'reset_password',
            token=token,
            _external=True
        )

        try:
            email_text = f"""Hello {user['username']},

We received a request to reset your SchemeAI password.

Click the link below to reset your password:

{reset_link}

If you did not request this password reset, you can ignore this email.

Regards,
SchemeAI Team
"""
            sent = send_email(
                target_email,
                "SchemeAI - Password Reset",
                email_text,
                from_email="jyothisreelakshmi129@gmail.com"
            )
            if sent:
                return render_template(
                    'forgot_password.html',
                    default_email=target_email,
                    success_msg=f'Password reset link has been sent to {target_email}.'
                )
            else:
                return render_template(
                    'forgot_password.html',
                    default_email=target_email,
                    error='Could not send the reset email. Please try again later.'
                )

        except Exception as e:
            print(f"Email sending error: {str(e)}")

            return render_template(
                'forgot_password.html',
                default_email=input_val,
                error='Could not send the reset email. Please try again later.'
            )

    return render_template('forgot_password.html', default_email=default_email)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        user_id = serializer.loads(
            token,
            salt='password-reset',
            max_age=1800
        )
    except SignatureExpired:
        return "Invalid or expired password reset link.", 400
    except BadSignature:
        return "Invalid or expired password reset link.", 400
    if request.method == 'POST':
        new_password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not new_password or not confirm_password:
            return render_template(
                'reset_password.html',
                error='All fields are required.'
            )

        if len(new_password) < 6:
            return render_template(
                'reset_password.html',
                error='Password must be at least 6 characters long.'
            )

        if new_password != confirm_password:
            return render_template(
                'reset_password.html',
                error='Passwords do not match.'
            )

        update_user_password(user_id, new_password)

        return redirect(url_for('login', reset='success'))

    return render_template('reset_password.html')

@app.route('/logout')
def logout():
    """
    Logs out the user and clears session tokens.
    """
    session.clear()
    return redirect(url_for('home'))

@app.route('/chat')
def chat_workspace():
    """
    Renders the dedicated chatbot workspace interface.
    Requires user authentication.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    return render_template('chat.html', username=session['username'])

@app.route('/schemes')
def schemes_catalog():
    """
    Displays government schemes catalog with category filtering and search.
    """
    logged_in = 'user_id' in session
    username = session.get('username')
    category_filter = request.args.get('category', '').strip().lower()
    search_q = request.args.get('q', '').strip().lower()
    
    all_schemes = get_all_schemes()
    filtered_schemes = []
    
    for s in all_schemes:
        cat = str(s.get('category', '')).lower()
        name = str(s.get('name', '')).lower()
        desc = str(s.get('description', '')).lower()
        
        cat_match = True
        if category_filter and category_filter != 'all':
            if category_filter in ['student', 'students']:
                cat_match = 'student' in cat
            elif category_filter in ['farmer', 'farmers']:
                cat_match = 'farmer' in cat or 'agri' in cat
            elif category_filter in ['women', 'woman']:
                cat_match = 'women' in cat or 'female' in cat
            elif category_filter in ['senior', 'senior_citizen', 'seniors']:
                cat_match = 'senior' in cat or 'pension' in cat
            elif category_filter in ['unemployed', 'youth']:
                cat_match = 'unemployed' in cat or 'skill' in cat or 'youth' in cat
            elif category_filter in ['disabled', 'disabled_citizens']:
                cat_match = 'disabled' in cat or 'handicap' in cat
            else:
                cat_match = category_filter in cat
                
        search_match = True
        if search_q:
            search_match = (search_q in name or search_q in desc or search_q in cat)
            
        if cat_match and search_match:
            filtered_schemes.append(s)
            
    return render_template(
        'schemes.html',
        schemes=filtered_schemes,
        logged_in=logged_in,
        username=username,
        active_category=category_filter or 'all',
        search_query=search_q,
        total_count=len(all_schemes)
    )

@app.route('/schemes/<int:scheme_id>')
def scheme_details(scheme_id):
    """
    Renders detailed information for a single government scheme.
    """
    logged_in = 'user_id' in session
    username = session.get('username')
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        return redirect(url_for('schemes_catalog'))
        
    return render_template(
        'scheme_details.html',
        scheme=scheme,
        logged_in=logged_in,
        username=username
    )

@app.route('/feedback', methods=['GET', 'POST'])
def feedback_page():
    """
    Renders dedicated feedback submission page and handles form post.
    """
    logged_in = 'user_id' in session
    username = session.get('username')
    success_msg = None
    error = None
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        
        if not name or not email or not message:
            error = "All fields are required."
        elif '@' not in email or '.' not in email:
            error = "Please provide a valid email address."
        else:
            try:
                save_feedback(name, email, message)
                notify_feedback_async(name, email, message)
                success_msg = "Thank you! Your feedback has been submitted successfully. A confirmation email has been sent to your inbox."
            except Exception as e:
                print(f"Feedback Save Error: {str(e)}")
                success_msg = "Thank you! Your feedback has been recorded."
                
    user = get_user_by_username(username) if username else None

    return render_template(
        'feedback.html',
        logged_in=logged_in,
        username=username,
        user=user,
        success_msg=success_msg,
        error=error
    )

@app.route('/profile')
def user_profile():
    """
    Renders the user dashboard and profile view.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    username = session['username']
    user = get_user_by_username(username)
    history = get_chat_history(user_id) or []
    
    return render_template(
        'profile.html',
        user=user,
        username=username,
        logged_in=True,
        chat_count=len(history)
    )

@app.route('/about')
def about_page():
    """
    Renders the About page explaining SchemeAI.
    """
    logged_in = 'user_id' in session
    username = session.get('username')
    return render_template('about.html', logged_in=logged_in, username=username)

# --- Chatbot API Routes ---

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """
    Processes chat requests, saves messages to SQLite, and fetches recommendations.
    """
    # 1. Authentication Check
    if 'user_id' not in session:
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized access. Please log in first.'
        }), 401
        
    user_id = session['user_id']
    
    # 2. Parse JSON Data Safely
    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Invalid query format. JSON with a message field is required.'
        }), 400
        
    user_message = data['message'].strip()
    
    # 3. Input Validation
    if not user_message:
        return jsonify({
            'status': 'error',
            'message': 'Message cannot be empty.'
        }), 400
        
    try:
        # 4. Save User Message to History Table
        save_chat_message(user_id, 'user', user_message)
        
        # 5. Generate Recommendation Response via matching algorithm
        bot_response_html = generate_recommendation_response(user_message)
        
        # 6. Save Bot Response to History Table
        save_chat_message(user_id, 'bot', bot_response_html)
        
        return jsonify({
            'status': 'success',
            'response': bot_response_html
        })
    except Exception as e:
        # Error handling for unexpected failures
        print(f"Chat API Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An unexpected database error occurred while processing your request.'
        }), 500

@app.route('/api/history', methods=['GET'])
def api_history():
    """
    Retrieves the logged-in user's chat history from the database.
    """
    if 'user_id' not in session:
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized access.'
        }), 401
        
    try:
        history = get_chat_history(session['user_id'])
        return jsonify({
            'status': 'success',
            'history': history
        })
    except Exception as e:
        print(f"History Fetch Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Could not retrieve chat history.'
        }), 500

@app.route('/api/clear', methods=['POST'])
def api_clear():
    """
    Deletes the logged-in user's chat history from the database.
    """
    if 'user_id' not in session:
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized access.'
        }), 401
        
    try:
        clear_chat_history(session['user_id'])
        return jsonify({
            'status': 'success',
            'message': 'Chat history successfully cleared.'
        })
    except Exception as e:
        print(f"History Clear Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Could not clear chat history.'
        }), 500

@app.route('/api/feedback', methods=['POST'])
def api_feedback():
    """
    Handles contact/feedback form submissions.
    Saves submission to SQLite and sends notification email to jyothisreelakshmi129@gmail.com via Gmail SMTP.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Invalid request format. JSON data is required.'
        }), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    message = data.get('message', '').strip()

    if not name or not email or not message:
        return jsonify({
            'status': 'error',
            'message': 'All fields (Name, Email, Message) are required.'
        }), 400

    if '@' not in email or '.' not in email:
        return jsonify({
            'status': 'error',
            'message': 'Please provide a valid email address.'
        }), 400

    try:
        # 1. Save to SQLite database
        save_feedback(name, email, message)

        # 2. Dispatch email notifications (admin alert + citizen confirmation)
        notify_feedback_async(name, email, message)

        return jsonify({
            'status': 'success',
            'message': 'Thank you! Your feedback has been submitted successfully. A confirmation email has been sent to your inbox.'
        })

    except Exception as e:
        print(f"Feedback processing error: {str(e)}")
        return jsonify({
            'status': 'success',
            'message': 'Thank you! Your feedback has been recorded successfully.'
        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)