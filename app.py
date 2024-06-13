from flask import Flask, request, render_template_string
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="141003",
    database="user_database"
)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        firstname = request.form['fName']
        middlename = request.form['mName']
        lastname = request.form['lName']
        username = request.form['username']
        password = request.form['password']
        contact = request.form['contactNo']
        emailid = request.form['email']
        loc = request.form['location']
        govtid = request.form['govtId']

        cursor = db.cursor()
        cursor.execute("INSERT INTO users (fname, mname, lname, uname, psw, contactno, email, location, govtid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (firstname, middlename, lastname, username, password, contact, emailid, loc, govtid))
        db.commit()
        cursor.close()

        return "Login successful"
    return render_template_string(r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register & Login</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
  </head>
<body>
    <div class="container" id="signup" style="display:none;">
      <h1 class="form-title">Register</h1>
      <form action="/login" method="post" >
        <div class="input-group">
          <i class="fas fa-user"></i>
          <input type="text" name="fName" id="fName" placeholder="First Name" required>
          <label for="fName">First Name</label>
        </div>
        <div class="input-group">
          <i class="fas fa-user"></i>
          <input type="text" name="mName" id="mName" placeholder="Middle Name" required>
          <label for="mName">Middle Name (if any)</label>
        </div>
        <div class="input-group">
          <i class="fas fa-user"></i>
          <input type="text" name="lName" id="lName" placeholder="Last Name" required>
          <label for="lName">Last Name</label>
        </div>
        <div class="input-group">
          <i class="fas fa-user"></i>
          <input type="text" name="username" id="username" placeholder="Username" required>
          <label for="username">Username</label>
        </div>
        <div class="input-group">
          <i class="fas fa-lock"></i>
          <input type="password" name="password" id="password" placeholder="Password" required>
          <label for="password">Password</label>
        </div>
        <div class="input-group">
          <i class="fa fa-phone" aria-hidden="true"></i>
          <input type="contactNo" name="contactNo" id="contactNo" placeholder="Contact No" required>
          <label for="contactNo">Contact No</label>
        </div>
        <div class="input-group">
          <i class="fas fa-envelope"></i>
          <input type="email" name="email" id="email" placeholder="Email" required>
          <label for="email">Email</label>
        </div>
        <div class="input-group">
          <i class="fa fa-globe" aria-hidden="true"></i>
          <input type="location" name="location" id="location" placeholder="Location" required>
          <label for="location">Location</label>
        </div>
        <div class="input-group">
          <i class="fa fa-id-card" aria-hidden="true"></i>
          <input type="govtId" name="govtId" id="govtId" placeholder="Government Id" required>
          <label for="govtId">Government Id</label>
        </div>
        
       <input type="submit" class="btn" value="Sign Up" name="signUp">
      </form>
      <p class="or">
        or
      </p>
      <div class="icons">
        <i class="fab fa-google"></i>
        <i class="fab fa-facebook"></i>
      </div>
      <div class="links">
        <p>Already Have Account ?</p>
        <button id="signInButton">Sign In</button>
      </div>
    </div>

    <div class="container" id="signIn">
        <h1 class="form-title">Sign In</h1>
        <form method="post" action="/login">
          <div class="input-group">
            <i class="fas fa-user"></i>
              <input type="username" name="username" id="username" placeholder="Username" required>
              <label for="username">Username</label>
          </div>
          <div class="input-group">
              <i class="fas fa-lock"></i>
              <input type="password" name="password" id="password" placeholder="Password" required>
              <label for="password">Password</label>
          </div>
          <p class="recover">
            <a href="#">Recover Password</a>
          </p>
         <input type="submit" class="btn" value="Sign In" name="signIn">
        </form>
        <p class="or">
          or
        </p>
        <div class="icons">
          <i class="fab fa-google"></i>
          <i class="fab fa-facebook"></i>
        </div>
        <div class="links">
          <p>Don't have account yet?</p>
          <button id="signUpButton">Sign Up</button>
        </div>
      </div>
      <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>''')

if __name__ == '__main__':
    app.run(debug=True)