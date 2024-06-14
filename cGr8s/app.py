from flask import Flask, request, render_template, redirect, url_for
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="141003",
    database="cgr8s"
)

@app.route('/')
def front_page():
    return render_template('front_page.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE uname=%s AND psw=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return "Login successful"
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullName']
        dob = request.form['date']
        password = request.form['password']
        email = request.form['email']
        contact = request.form['contactNo']
        location = request.form['location']
        govtid = request.form['govtId']

        cursor = db.cursor()
        cursor.execute("INSERT INTO users (fname, dob, psw, email, contactno, location, govt) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                       (fullname, dob, password, email, contact, location, govtid))
        db.commit()
        cursor.close()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/candidate')
def candidate():
    return render_template('candidate.html')

@app.route('/employer')
def employer():
    return render_template('employer.html')

if __name__ == '__main__':
    app.run(debug=True)
