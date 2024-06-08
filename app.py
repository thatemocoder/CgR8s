from flask import Flask, request, render_template_string
import mysql.connector

app = Flask(__name__)

# MySQL database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="141003",
    database="user_database"
)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['psw']

        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        cursor.close()

        return "Login successful"
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Page</title>
        </head>
        <body>
            <h2>Login Form</h2>
            <form action="/login" method="post">
                <div class="container">
                    <label for="uname"><b>Username</b></label>
                    <input type="text" placeholder="Enter Username" name="uname" required>
                    <label for="psw"><b>Password</b></label>
                    <input type="password" placeholder="Enter Password" name="psw" required>
                    <button type="submit">Login</button>
                </div>
            </form>
        </body>
        </html>
    ''')

if __name__ == '__main__':
    app.run(debug=True)
