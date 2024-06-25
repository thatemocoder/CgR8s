from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os  # Import for file operations
from werkzeug.utils import secure_filename  # Import for secure file name generation

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'  # Folder to store uploaded CVs
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}  # Allowed file extensions for CVs

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="141003",
    database="cgr8s"
)

# Function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to generate OTP
def generate_otp(length=6):
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp

# Function to send email
def send_email(otp, recipient_email):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "ujan.pal2003@gmail.com"
    sender_password = "ccsd yoan dbne agdq"

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
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to verify OTP
def verify_otp(input_otp, actual_otp):
    return input_otp == actual_otp

@app.route('/')
def front_page():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute("SELECT psw FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[0], password):
            return "Login successful"
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullName']
        email = request.form['email']
        password = request.form['password']
        contact = request.form['contactNo']
        role = 'employer'  # Set role to employer

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        cursor = db.cursor()

        # Check if the email already exists
        cursor.execute("SELECT email FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return "Email already exists. Please use a different email address."

        # Insert the new user if email does not exist
        try:
            cursor.execute(
                "INSERT INTO users (fname, email, psw, contactno, role) VALUES (%s, %s, %s, %s, %s)",
                (fullname, email, hashed_password, contact, role)
            )
            user_id = cursor.lastrowid
            db.commit()

            otp = generate_otp()
            otp_expiry = datetime.now() + timedelta(minutes=10)
            cursor.execute(
                "INSERT INTO otp_verification (user_id, email, otp, otp_expiry, is_verified) VALUES (%s, %s, %s, %s, %s)",
                (user_id, email, otp, otp_expiry, 'NO')
            )
            db.commit()
            cursor.close()

            send_email(otp, email)

            return redirect(url_for('verify_email', email=email))

        except mysql.connector.Error as err:
            cursor.close()
            print(f"Failed to insert user: {err}")
            return "Failed to register. Please try again later."

    return render_template('register.html')

@app.route('/register_candidate', methods=['POST'])
def register_candidate():
    if request.method == 'POST':
        fullname = request.form['fullName']
        email = request.form['email']
        password = request.form['password']
        contact = request.form['contactNo']

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Check if the email already exists
        cursor = db.cursor()
        cursor.execute("SELECT email FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return "Email already exists. Please use a different email address."

        # Handle CV file upload
        if 'cv' not in request.files:
            cursor.close()
            return "No file part"

        cv_file = request.files['cv']

        if cv_file.filename == '':
            cursor.close()
            return "No selected file"

        if cv_file and allowed_file(cv_file.filename):
            filename = secure_filename(cv_file.filename)
            cv_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(f"CV saved successfully: {filename}")
        else:
            cursor.close()
            return "Invalid file type. Allowed type is only pdfs"

        # Insert the new user if email does not exist
        try:
            cursor.execute(
                "INSERT INTO users (fname, email, psw, contactno, role) VALUES (%s, %s, %s, %s, %s)",
                (fullname, email, hashed_password, contact, 'candidate')
            )
            user_id = cursor.lastrowid
            db.commit()

            otp = generate_otp()
            otp_expiry = datetime.now() + timedelta(minutes=10)
            cursor.execute(
                "INSERT INTO otp_verification (user_id, email, otp, otp_expiry, is_verified) VALUES (%s, %s, %s, %s, %s)",
                (user_id, email, otp, otp_expiry, 'NO')
            )
            db.commit()
            cursor.close()

            send_email(otp, email)

            return redirect(url_for('verify_email', email=email))
        
        except mysql.connector.Error as err:
            cursor.close()
            print(f"Failed to insert user: {err}")
            return "Failed to register. Please try again later."

    return "Invalid request"

@app.route('/select_role', methods=['GET', 'POST'])
def select_role():
    return render_template('select_role.html')

@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    email = request.args.get('email')
    if request.method == 'POST':
        input_otp = request.form['otp']
        
        cursor = db.cursor()
        cursor.execute("""
            SELECT ov.otp, ov.otp_expiry, ov.is_verified
            FROM otp_verification ov
            JOIN users u ON ov.user_id = u.id
            WHERE u.email = %s
        """, (email,))
        user_otp = cursor.fetchone()
        cursor.close()

        if user_otp:
            otp, otp_expiry, is_verified = user_otp

            if is_verified == 'YES':
                return "Email already verified."

            # Check if OTP is valid and not expired
            if datetime.now() < otp_expiry and verify_otp(input_otp, otp):
                cursor = db.cursor()
                cursor.execute("""
                    UPDATE otp_verification
                    JOIN users u ON otp_verification.user_id = u.id
                    SET otp_verification.is_verified = 'YES'
                    WHERE u.email = %s
                """, (email,))
                db.commit()
                cursor.close()
                return "Email verified successfully!"
            else:
                return "Invalid or expired OTP."
        else:
            return "User not found or OTP expired."

    return render_template('verify_otp.html', email=email)

if __name__ == '__main__':
    app.run(debug=True)