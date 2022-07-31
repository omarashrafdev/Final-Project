# Import needed functions
from crypt import methods
import os
import smtplib

from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from cs50 import SQL
from datetime import date
from werkzeug.security import check_password_hash, generate_password_hash
from random import randint
from functions import login_required, strong_password_check, Years_Between

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded and enable debug mode
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.run(debug=True)

# Declare GLOBAL varable for the email verification function
CODE = randint(111111, 999999)

# Store the URL generated with the secret key from the environment variable to the program
#s = URLSafeTimedSerializer(os.environ["SECRET_KEY"])

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

# Egyption's CITIES list
CITIES = ["Alexandria", "Aswan", "Asyut", "Beheira", "Beni Suef", "Cairo", "Dakahlia", "Damietta", "Faiyum", "Gharbia", "Giza", "Ismailia", "Kafr El Sheikh", "Luxor", "Matruh", "Minya", "Monufia", "New Valley", "North Sinai", "Port Said", "Qalyubia ", "Qena", "Red Sea", "Sharqia", "Sohag", "South Sinai", "Suez"]

# Today's date to pass to the forms
TODAY = date.today()

# Doctor Check (1=True, 0=False)
IS_DOCTOR = 0
# Email Verify Check (1=True, 0=False)
IS_VERIFIED = 0


@app.route("/")
@login_required
def index():
    # Essential variables
    user_id = session["user_id"]
    
    # Return homapege view
    return render_template("index.html")


@app.route("/Register", methods=["GET", "POST"])
def Register():
    # Clear the current session
    session.clear()

    if request.method == "GET":
        return render_template("Register.html",  CITIES=CITIES)
    else:
        # Data input from the form
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        city = request.form.get("city")
        username = request.form.get("username")
        date_of_birth = request.form.get("date_of_birth")
        
        # Validate username duplication
        data = db.execute("SELECT * FROM users WHERE username = ? AND is_doctor = TRUE", username)
        if len(data) != 0:
            return render_template("Register.html", error="Username already in use. Please try another one.", 
                                     CITIES=CITIES)
        
        # Validate email duplication
        data = db.execute("SELECT * FROM users WHERE email = ? AND is_doctor = TRUE", email)
        if len(data) != 0:
            return render_template("Register.html", error="Email Address is already in use. Please try another one.", 
                                     CITIES=CITIES)
        
        # Validate phone number duplication
        data = db.execute("SELECT * FROM users WHERE phone_number = ? AND is_doctor = TRUE", phone_number)
        if len(data) != 0:
            return render_template("Register.html", error="Phone number is already in use. Please try another one.", 
                                     CITIES=CITIES)
            
        # Validate user's age (older than 15)
        if Years_Between(date_of_birth, TODAY) < 15:
            return render_template("Register.html", error="You have to be older than 15 years old to use", 
                                     CITIES=CITIES)
        
        # Validate password match
        if request.form.get("password1") != request.form.get("password2"):
            return render_template("Register.html", error="Passwords don't match. Please try again.", 
                                     CITIES=CITIES)

        # Validate password strength
        password = request.form.get("password1")
        if strong_password_check(password) == 1:
            return render_template("Register.html", error="Please choose a more secure password. It should be longer than 6 characters, unique to you and difficult for others to guess.", CITIES=CITIES)
        elif strong_password_check(password) == 2:
            return render_template("Register.html", error="Your password must be at least 8 characters long. Please try another.", CITIES=CITIES)
        password_hash = generate_password_hash(password)
        
        # Store profile pic in static media
        profile_picture = request.files['profile_picture[]']
        profile_picture.save("static/media/profile_picture.png")
        
        # Store user's data in the database
        with open ("static/media/profile_picture.png", "rb") as pic:
            db.execute("INSERT INTO users (username, password_hash, first_name, last_name, city, phone_number, email, is_doctor, date_of_birth, profile_picture, is_verified) VALUES (?,?,?,?,?,?,?,TRUE,?,?,FALSE)",
                username, password_hash, first_name, last_name, city, phone_number, email, date_of_birth, pic.read())
            
        # Session variables
        session["user_id"] = db.execute("SELECT * FROM users WHERE username = ?", username)[0]["id"]
        session["name"] = first_name + " " + last_name
        
        # Redirect to home page
        return redirect("/")
        
        

@app.route("/Login", methods=["GET", "POST"])
def login():
    # Clear the current session
    session.clear()

    if request.method == "GET":
        return render_template("Login.html")
    else:
        # Get username and password
        username = request.form.get("username")
        password = request.form.get("password")
        
        data = db.execute("SELECT * FROM users WHERE username = ? AND is_doctor = TRUE", username)
        
        # Validate username
        if len(data) != 1:
            return render_template("Login.html", error="Couldn't find user. Please try again.")
        
        # Validate password
        if not check_password_hash(data[0]["password_hash"], password):
            return render_template("Login.html", error="Wrong password. Please try again.")
        
        # Store the user id in the session's data
        session["user_id"] = data[0]["id"]
        session["name"] = data[0]["first_name"] + " " + data[0]["last_name"]
        
        # Store the profile picture
        with open("static/media/profile_picture.png", "wb") as pic:
            profile_binary = db.execute("SELECT profile_picture FROM users WHERE id=?", session["user_id"])[0]["profile_picture"]
            pic.write(profile_binary)
            
        return redirect("/")
    

@app.route("/Logout")
def logout():
    # Clear the existing session
    session.clear()
    
    # Delete profile picture
    if os.path.exists("static/media/profile_picture.png"):
        os.remove("static/media/profile_picture.png")

    # Redirect user to login form
    return redirect("/")


@app.route("/Settings")
def settings():
    return render_template("settings.html")


@app.route("/Profile-<int:id>")
def profile(id):
    data = db.execute("SELECT * FROM users WHERE id=?", id)
    return render_template("profile.html", data=data)


@app.route("/ChangePassword", methods=["GET", "POST"])
def change_password():
    if request.method == "GET":
        return render_template("change_password.html")
    else:
        # Get old password from the user
        old_password = request.form.get("old_password")
        
        # Validate current password
        data = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if not check_password_hash(data[0]["password_hash"], old_password):
            return render_template("change_password.html", error="Wrong password. Please try again.")
        
        # Validate passwords match
        if request.form.get("password1") != request.form.get("password2"):
            return render_template("change_password.html", error="Passwords must match. Please try again.")
        
        # Validate password strength
        password = request.form.get("password1")
        if strong_password_check(password) == 1:
            return render_template("change_password.html", error="Please choose a more secure password. It should be longer than 6 characters, unique to you and difficult for others to guess.")
        elif strong_password_check(password) == 2:
            return render_template("change_password.html", error="Your password must be at least 8 characters long. Please try another.")

        # Update DB to the new password
        password_hash = generate_password_hash(password)
        db.execute("UPDATE users SET password_hash=? WHERE id=?", password_hash, session["user_id"])
        
        # Return the success message to the user
        return render_template("change_password.html", success="Password changed successfully.")
        

@app.route("/ChangeEmail", methods=["GET", "POST"])
def change_email():
    if request.method == "GET":
        return render_template("change_email.html")
    else:
        # Get the new email from the user
        email = request.form.get("email")
        
        # Validate email duplication
        data = db.execute("SELECT * FROM users WHERE email=?", email)
        if len(data) != 0:
            return render_template("change_email.html", error="Email already in use. Please try again.")

        # The message
        message = "\nThis is your code: " + str(CODE)
        
        # Send message to the new email
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(os.environ["EMAIL"], os.environ["PASSWORD"])
        server.sendmail(os.environ["EMAIL"], email, message)
        server.close()
        
        # Redirect to the verify function to verify the new email with the code
        return redirect(url_for("verify_new_email", email=email))
    

@app.route("/VerifyNewEmail/<email>", methods=["GET", "POST"])
def verify_new_email(email):
    if request.method == "GET":
        return render_template("verify_new_email.html", email=email)
    else:
        # Get the code the user has entered
        code = int(request.form.get("code"))

        # Validate code
        if code != CODE:
            return render_template("verify_new_email.html", error="Wrong code. New one was sent.", email=email)
        
        # Update the email in the database
        db.execute("UPDATE users SET email=? WHERE id=?", email, session["user_id"])
        
        # Redirect to home page
        return redirect("/")
    

@app.route("/EditInfo", methods=["GET", "POST"])
def edit_info():
    if request.method == "GET":
        return render_template("pending.html")
    else:
        ...
    