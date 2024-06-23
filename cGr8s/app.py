# from flask import Flask, request, render_template, redirect, url_for, session
# import mysql.connector
# from werkzeug.security import generate_password_hash, check_password_hash
# import random
# import smtplib
# from email.mime.text import MIMEText
# from datetime import datetime, timedelta

# app = Flask(__name__)
# app.secret_key = 'supersecretkey'

# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="141003",
#     database="cgr8s"
# )

# def generate_otp(length=6):
#     otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
#     return otp

# def send_email(otp, recipient_email):
#     smtp_server = "smtp.gmail.com"
#     smtp_port = 587
#     sender_email = "ujan.pal2003@gmail.com"
#     sender_password = "ccsd yoan dbne agdq"

#     subject = "Your OTP Code"
#     body = f"Your OTP code is {otp}. It will expire in 10 minutes."
#     msg = MIMEText(body)
#     msg['Subject'] = subject
#     msg['From'] = sender_email
#     msg['To'] = recipient_email

#     try:
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(sender_email, sender_password)
#             server.sendmail(sender_email, recipient_email, msg.as_string())
#             print("Email sent successfully.")
#     except Exception as e:
#         print(f"Failed to send email: {e}")

# def verify_otp(input_otp, actual_otp):
#     return input_otp == actual_otp

# @app.route('/')
# def front_page():
#     return render_template('front_page.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']

#         cursor = db.cursor()
#         cursor.execute("SELECT psw FROM users WHERE email=%s", (email,))
#         user = cursor.fetchone()
#         cursor.close()

#         if user and check_password_hash(user[0], password):
#             return "Login successful"
#         else:
#             return "Invalid credentials"
#     return render_template('login.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         fullname = request.form['fullName']
#         email = request.form['email']
#         password = request.form['password']
#         contact = request.form['contactNo']
#         role = session.get('role')

#         if not role:
#             return "Role is missing. Please select your role first."

#         hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

#         cursor = db.cursor()

#         # Check if the email already exists
#         cursor.execute("SELECT email FROM users WHERE email=%s", (email,))
#         existing_user = cursor.fetchone()

#         if existing_user:
#             cursor.close()
#             return "Email already exists. Please use a different email address."

#         # Insert the new user if email does not exist
#         try:
#             cursor.execute(
#                 "INSERT INTO users (fname, email, psw, contactno, role) VALUES (%s, %s, %s, %s, %s)",
#                 (fullname, email, hashed_password, contact, role)
#             )
#             user_id = cursor.lastrowid
#             db.commit()

#             otp = generate_otp()
#             otp_expiry = datetime.now() + timedelta(minutes=10)
#             cursor.execute(
#                 "INSERT INTO otp_verification (user_id, email, otp, otp_expiry, is_verified) VALUES (%s, %s, %s, %s, %s)",
#                 (user_id, email, otp, otp_expiry, 'NO')
#             )
#             db.commit()
#             cursor.close()

#             send_email(otp, email)

#             return redirect(url_for('verify_email', email=email))
        
#         except mysql.connector.Error as err:
#             cursor.close()
#             print(f"Failed to insert user: {err}")
#             return "Failed to register. Please try again later."
    
#     role = session.get('role', 'candidate')
#     return render_template('register.html', role=role)

# @app.route('/select_role', methods=['GET', 'POST'])
# def select_role():
#     if request.method == 'POST':
#         role = request.form['role']
#         session['role'] = role
#         return redirect(url_for('register'))
#     return render_template('select_role.html')

# @app.route('/verify_email', methods=['GET', 'POST'])
# def verify_email():
#     email = request.args.get('email')
#     if request.method == 'POST':
#         input_otp = request.form['otp']
        
#         cursor = db.cursor()
#         cursor.execute("""
#             SELECT ov.otp, ov.otp_expiry, ov.is_verified
#             FROM otp_verification ov
#             JOIN users u ON ov.user_id = u.id
#             WHERE u.email = %s
#         """, (email,))
#         user_otp = cursor.fetchone()
#         cursor.close()

#         if user_otp:
#             otp, otp_expiry, is_verified = user_otp

#             if is_verified == 'YES':
#                 return "Email already verified."

#             # Check if OTP is valid and not expired
#             if datetime.now() < otp_expiry and verify_otp(input_otp, otp):
#                 cursor = db.cursor()
#                 cursor.execute("""
#                     UPDATE otp_verification
#                     JOIN users u ON otp_verification.user_id = u.id
#                     SET otp_verification.is_verified = 'YES'
#                     WHERE u.email = %s
#                 """, (email,))
#                 db.commit()
#                 cursor.close()
#                 return "Email verified successfully!"
#             else:
#                 return "Invalid or expired OTP."
#         else:
#             return "User not found or OTP expired."

#     return render_template('verify_otp.html', email=email)

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="141003",
    database="cgr8s"
)

def generate_otp(length=6):
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp

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
        role = session.get('role')

        if not role:
            return "Role is missing. Please select your role first."

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
    
    role = session.get('role', 'candidate')
    return render_template('register.html', role=role)

@app.route('/select_role', methods=['GET', 'POST'])
def select_role():
    if request.method == 'POST':
        role = request.form['role']
        session['role'] = role
        return redirect(url_for('register'))
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

@app.route('/google-signin', methods=['POST'])
def google_signin():
    token = request.json.get('id_token')
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']
        email = idinfo['email']
        name = idinfo['name']
        # Process the user info (e.g., create a new account or log them in)

        return jsonify({'status': 'success', 'userid': userid, 'email': email, 'name': name})

    except ValueError:
        # Invalid token
        return jsonify({'status': 'error', 'message': 'Invalid token'}), 400

if __name__ == '__main__':
    app.run(debug=True)