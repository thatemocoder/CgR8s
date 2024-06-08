from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from werkzeug.security import check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database configuration
db_config = {
    'user': 'u629519980_root',
    'password': 'b1239potK',
    'host': 'localhost',
    'database': 'u629519980_credentials'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

@app.route('/', methods=['GET', 'POST'])
def login():
    errors = []
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Validate form data
        if not email:
            errors.append("Email is required")
        elif not validate_email(email):
            errors.append("Invalid email format")

        if not password:
            errors.append("Password is required")

        if not errors:
            # Check login credentials
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and check_password_hash(user['password'], password):
                return redirect(url_for('seeme'))
            else:
                errors.append("Invalid email or password")

    return render_template('login.html', errors=errors)

@app.route('/seeme')
def seeme():
    return "Login successful! You are now seeing the secret page."

def validate_email(email):
    import re
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

if __name__ == '__main__':
    app.run(debug=True)
