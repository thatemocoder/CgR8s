import subprocess
import sys
from flask import Flask, request, render_template, redirect, url_for, session, jsonify, g
import mysql.connector
import json
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from google.cloud import recaptchaenterprise_v1
from google.cloud.recaptchaenterprise_v1 import Assessment
from google.oauth2 import id_token
from google.auth.transport import requests
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def install_requirements():
    try:
        # Install the requirements from requirements.txt
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        # Create a flag file to indicate that requirements are installed
        with open('requirements_installed.flag', 'w') as f:
            f.write('installed')
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing the packages: {e}")
        sys.exit(1)

def create_assessment(
    project_id: str, recaptcha_key: str, token: str, recaptcha_action: str
) -> Assessment:
    """Create an assessment to analyse the risk of a UI action.
    Args:
        project_id: Your Google Cloud project ID.
        recaptcha_key: The reCAPTCHA key associated with the site/app
        token: The generated token obtained from the client.
        recaptcha_action: Action name corresponding to the token.
    """

    client = recaptchaenterprise_v1.RecaptchaEnterpriseServiceClient()

    # Set the properties of the event to be tracked.
    event = recaptchaenterprise_v1.Event()
    event.site_key = recaptcha_key
    event.token = token

    assessment = recaptchaenterprise_v1.Assessment()
    assessment.event = event

    project_name = f"projects/{project_id}"

    # Build the assessment request.
    request = recaptchaenterprise_v1.CreateAssessmentRequest()
    request.assessment = assessment
    request.parent = project_name

    response = client.create_assessment(request)

    # Check if the token is valid.
    if not response.token_properties.valid:
        print(
            "The CreateAssessment call failed because the token was "
            + "invalid for the following reasons: "
            + str(response.token_properties.invalid_reason)
        )
        return

    # Check if the expected action was executed.
    if response.token_properties.action != recaptcha_action:
        print(
            "The action attribute in your reCAPTCHA tag does"
            + "not match the action you are expecting to score"
        )
        return
    else:
        # Get the risk score and the reason(s).
        # For more information on interpreting the assessment, see:
        # https://cloud.google.com/recaptcha-enterprise/docs/interpret-assessment
        for reason in response.risk_analysis.reasons:
            print(reason)
        print(
            "The reCAPTCHA score for this token is: "
            + str(response.risk_analysis.score)
        )
        # Get the assessment name (ID). Use this to annotate the assessment.
        assessment_name = client.parse_assessment_path(response.name).get("assessment")
        print(f"Assessment name: {assessment_name}")
    return response

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="141003",
    database="cgr8s"
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_otp(length=6):
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp

def send_email(otp, recipient_email):
    smtp_server = "mail.cgr8s.com"
    smtp_port = 587
    sender_email = "noreply@cgr8s.com"
    sender_password = "ktrNahVu=pwF"

    subject = "Your OTP Code"
    body = f"Your OTP code is {otp}. It will expire in 10 minutes."
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Email sent successfully.")
        return True
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
        return False
    
def check_email_exists(email):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
    exists = cursor.fetchone()[0] > 0
    cursor.close()
    return exists

@app.route('/check_email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email')
    if check_email_exists(email):
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})

@app.before_request
def load_user():
    if 'user_id' in session:
        g.user_id = session['user_id']
    else:
        g.user_id = None

# def alter_jobs_table():
#     cursor = db.cursor()
#     cursor.execute("SHOW COLUMNS FROM jobs LIKE 'applicants'")
#     result = cursor.fetchone()
#     if not result:
#         cursor.execute("ALTER TABLE jobs ADD COLUMN applicants JSON")
#     db.commit()
#     cursor.close()

# alter_jobs_table()

@app.context_processor
def inject_user():
    return dict(user_id=g.user_id)

@app.route('/')
def front_page():
    cursor = db.cursor()
    
    # Check if the users table exists, and create it if it doesn't
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fullname VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        country_code VARCHAR(10) NOT NULL,
        mobile_number VARCHAR(20) NOT NULL,
        work_status ENUM('experienced', 'fresher'),
        cv_filename VARCHAR(255) NOT NULL,
        role ENUM('candidate', 'employer') NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Check if the jobs table exists, and create it if it doesn't
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        job_title VARCHAR(255) NOT NULL,
        job_type ENUM('Full Time', 'Part Time', 'Contract') NOT NULL,
        job_location ENUM('On Site', 'Remote', 'Hybrid') NOT NULL,
        job_description TEXT NOT NULL,
        keywords VARCHAR(255) NOT NULL,
        vacancies INT NOT NULL,
        job_country ENUM('UAE', 'Saudi Arabia', 'Qatar') NOT NULL,
        industry VARCHAR(255) NOT NULL,
        functional_area VARCHAR(255) NOT NULL,
        currency ENUM('AED', 'SAR', 'QAR') NOT NULL,
        salary_min DECIMAL(10, 2) NOT NULL,
        salary_max DECIMAL(10, 2) NOT NULL,
        hide_salary BOOLEAN DEFAULT FALSE,
        benefits TEXT,
        questions TEXT,
        company_profile TEXT NOT NULL,
        contact_person VARCHAR(255) NOT NULL,
        contact_designation VARCHAR(255) NOT NULL,
        company_address TEXT NOT NULL,
        hide_employer_details BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscription_list (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        role ENUM('candidate', 'employer') NOT NULL,
        subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    db.commit()
    cursor.close()

    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    if g.user_id:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (g.user_id,))
        user = cursor.fetchone()
        cursor.close()
        return render_template('landing.html', user=user)
    return render_template('landing.html', user=None)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in
    
    user_id = session['user_id']
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT fullname, email, mobile_number, country_code FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return render_template('profile.html', user=user)
    else:
        return "User not found", 404


@app.route('/landing_employer')
def front_page_employer():
    return render_template('landing_employer.html')

@app.route('/register_employer')
def register_employer():
    return render_template('register_employer.html')

@app.route('/job_posting')
def job_posting():
    return render_template('job_posting.html')

@app.route('/manage_jobs')
def manage_jobs():
    return render_template('manage_jobs.html')

@app.route('/job_search')
def job_search():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()
    cursor.close()
    return render_template('job_search.html', jobs=jobs)

@app.route('/interview_scheduler')
def interview_scheduler():
    return render_template('interview_scheduler.html')

@app.route('/submit_job', methods=['POST'])
def submit_job():
    if request.method == 'POST':
        user_id = session.get('user_id')  # Retrieve user_id from session
        
        if not user_id:
            return jsonify(success=False, message="User not logged in"), 401
        
        job_title = request.form['jobTitle']
        job_type = request.form['jobType']
        job_location = request.form['jobLocation']
        job_description = request.form['jobDescription']
        keywords = request.form['keywords']
        vacancies = request.form['vacancies']
        job_country = request.form['jobCountry']
        industry = request.form['industry']
        functional_area = request.form['functionalArea']
        currency = request.form['currency']
        salary_min = request.form['salaryMin']
        salary_max = request.form['salaryMax']
        hide_salary = 'hideSalary' in request.form
        benefits = request.form['benefits']
        questions = request.form['questions']
        company_profile = request.form['companyProfile']
        contact_person = request.form['contactPerson']
        contact_designation = request.form['contactDesignation']
        company_address = request.form['companyAddress']
        hide_employer_details = 'hideEmployerDetails' in request.form

        cursor = db.cursor()
        query = """
            INSERT INTO jobs (
                user_id, job_title, job_type, job_location, job_description, keywords, vacancies, job_country, 
                industry, functional_area, currency, salary_min, salary_max, hide_salary, benefits, questions, 
                company_profile, contact_person, contact_designation, company_address, hide_employer_details
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            user_id, job_title, job_type, job_location, job_description, keywords, vacancies, job_country, 
            industry, functional_area, currency, salary_min, salary_max, hide_salary, benefits, questions, 
            company_profile, contact_person, contact_designation, company_address, hide_employer_details
        ))
        db.commit()
        cursor.close()

        return redirect(url_for('front_page'))

    return render_template('job_posting.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')

            cursor = db.cursor()
            cursor.execute("SELECT id, password FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
            cursor.close()

            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]  # Store user ID in session
                return jsonify(success=True, message="Login successful")
            else:
                return jsonify(success=False, message="Invalid credentials")
        else:
            return jsonify(success=False, message="Request must be JSON"), 415
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['fullName']
        email = request.form['email']
        password = request.form['password']
        contact_no = request.form['contactNo']
        country_code = request.form['countryCode']
        work_status = request.form['workStatus']
        resume = request.files['cv']
        receive_updates = 'updates' in request.form

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        cursor = db.cursor()
        cursor.execute("SELECT email FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return "Email already exists. Please use a different email address."

        if resume and allowed_file(resume.filename):
            filename = secure_filename(resume.filename)
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resume.save(resume_path)
        else:
            return jsonify({'success': False, 'message': 'Invalid file format'})

        cursor = db.cursor()
        query = """
            INSERT INTO users (fullname, email, password, country_code, mobile_number, work_status, cv_filename, role) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'candidate')
        """
        cursor.execute(query, (full_name, email, hashed_password, country_code, contact_no, work_status, resume_path))
        db.commit()

        # Add to subscription_list if checkbox is checked
        if receive_updates:
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO subscription_list (email, role) VALUES (%s, 'candidate')
            """, (email,))
            db.commit()

        return redirect(url_for('profile'))

    return render_template('register.html')

# List of domains to be blocked
blocked_domains = [
    "@gmail.com", "@outlook.com", "@yahoo.com", "@icloud.com", "@protonmail.com",
    "@zoho.com", "@aol.com", "@gmx.com", "@yandex.com", "@yandex.ru", "@mail.com"
]

@app.route('/employer_register', methods=['GET', 'POST'])
def employer_register():
    if request.method == 'POST':
        company_name = request.form['fullName']
        email = request.form['email']
        password = request.form['password']
        contact_no = request.form['contactNo']
        country_code = request.form['countryCode']
        business_license = request.files['businessLicense']

        # Check if the email has a blocked domain
        if any(email.endswith(domain) for domain in blocked_domains):
            return jsonify(success=False, message="Email domain is not allowed. Use company domain.")

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        cursor = db.cursor()
        cursor.execute("SELECT email FROM users WHERE email=%s", (email,))
        existing_employer = cursor.fetchone()

        if existing_employer:
            cursor.close()
            return jsonify(success=False, message="Email already exists. Please use a different email address.")

        if business_license and allowed_file(business_license.filename):
            filename = secure_filename(business_license.filename)
            business_license_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            business_license.save(business_license_path)
        else:
            return jsonify({'success': False, 'message': 'Invalid file format'})

        cursor = db.cursor()
        query = """
            INSERT INTO users (fullname, email, password, country_code, mobile_number, cv_filename, role) VALUES (%s, %s, %s, %s, %s, %s, "employer")
        """
        cursor.execute(query, (company_name, email, hashed_password, country_code, contact_no, business_license_path))
        db.commit()

        return redirect(url_for('front_page'))

    return render_template('employer_register.html')

@app.route('/send_otp', methods=['POST'])
def send_otp():
    email = request.form['email']
    otp = generate_otp()

    session['otp'] = otp
    session['otp_expiry'] = (datetime.now() + timedelta(minutes=10)).isoformat()  # Save as string

    success = send_email(otp, email)
    print(f"send_email result: {success}")
    if success:
        return jsonify({'success': True, 'message': 'OTP sent successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send OTP'})

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    otp = data.get('otp')
    email = data.get('email')

    stored_otp = session.get('otp')
    otp_expiry = session.get('otp_expiry')

    if stored_otp and otp_expiry:
        otp_expiry = datetime.fromisoformat(otp_expiry)  # Convert the string to a datetime object
        if datetime.now() <= otp_expiry.replace(tzinfo=None):  # Make otp_expiry naive
            if otp == stored_otp:
                return jsonify({'success': True, 'message': 'OTP verified successfully'})
            else:
                return jsonify({'success': False, 'message': 'Invalid OTP'})
        else:
            return jsonify({'success': False, 'message': 'OTP expired or not found'})

    return jsonify({'success': False, 'message': 'OTP expired or not found'})

@app.route('/quick_apply', methods=['POST'])
def quick_apply():
    if 'user_id' not in session:
        return jsonify(success=False, message="User not logged in"), 401

    user_id = session['user_id']
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT fullname FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        return jsonify(success=False, message="User not found"), 404

    user_name = user['fullname']
    
    data = request.get_json()
    job_id = data.get('jobId')

    print(f"Received Job ID: {job_id}")  # Debugging output

    cursor.execute("SELECT applicants FROM jobs WHERE id = %s", (job_id,))
    job = cursor.fetchone()

    if not job:
        print(f"Job ID {job_id} not found in database.")  # Debugging output
        cursor.close()
        return jsonify(success=False, message="Job not found"), 404

    # If the applicants field is None or empty, initialize it with an empty list
    applicants = json.loads(job['applicants']) if job['applicants'] else []
    applicants.append({'user_id': user_id, 'user_name': user_name})

    print(f"Applicants before update: {applicants}")  # Debugging output

    cursor.execute("UPDATE jobs SET applicants = %s WHERE id = %s", (json.dumps(applicants), job_id))
    db.commit()
    cursor.close()

    print(f"Job {job_id} updated successfully.")  # Debugging output

    return jsonify(success=True, message="Applied successfully")

# Google OAuth setup
GOOGLE_CLIENT_ID = '60982637815-2hgv97anvmfn2f7ni9eabp65l0ccpbgk.apps.googleusercontent.com'  # Replace with your Google Client ID
GOOGLE_CLIENT_SECRET = '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'
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Function to validate Google Sign-In token
def validate_google_token(token):
    try:
        # Specify the CLIENT_ID of the app that accesses the backend
        id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        
        # ID token is valid. Get the user's Google Account information
        user_id = id_info['sub']
        email = id_info['email']
        name = id_info['name']

        return {
            "user_id": user_id,
            "email": email,
            "name": name
        }
    except ValueError:
        # Invalid token
        return None

# Google login route
@app.route('/google_login', methods=['POST'])
def google_login():
    token = request.form['idtoken']  # ID token from the client
    user_info = validate_google_token(token)

    if user_info:
        # Check if the user exists in the database, if not, create a new user
        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE email=%s", (user_info['email'],))
        user = cursor.fetchone()

        if not user:
            # Register new user
            cursor.execute("""
                INSERT INTO users (fullname, email, password, role) 
                VALUES (%s, %s, %s, %s)
            """, (user_info['name'], user_info['email'], None, 'candidate'))
            db.commit()

            # Retrieve the new user id
            user_id = cursor.lastrowid
        else:
            user_id = user[0]

        session['user_id'] = user_id  # Set user ID in session
        cursor.close()

        return jsonify(success=True, message="Google Sign-In successful")
    else:
        return jsonify(success=False, message="Invalid Google token"), 401

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user from session
    return redirect(url_for('front_page'))  # Redirect to front page after logout

if __name__ == '__main__':
    if not os.path.exists('requirements_installed.flag'):
        install_requirements()
    app.run(debug=True)