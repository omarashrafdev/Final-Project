# Import needed functions
from crypt import methods
from email import message
import os
import smtplib

from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from cs50 import SQL
from datetime import date
from werkzeug.security import check_password_hash, generate_password_hash
from random import randint
from functions import login_required, doctors_only, strong_password_check, Years_Between, generate_random_number

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded and enable debug mode
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.run(debug=True)

# Declare GLOBAL varable for the email verification function
CODE = randint(111111, 999999)
TEMP_CODE = 0

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


@app.route("/")
@login_required
def index():
    # Essential variables
    user_id = session["user_id"]

    # Verify email if not verified
    if not db.execute("SELECT is_verified FROM users WHERE id=?", user_id)[0]["is_verified"]:
        return redirect("/Rigster/EmailVerify")
    
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
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        city = request.form.get("city")
        username = request.form.get("username")
        date_of_birth = request.form.get("date_of_birth")
        user_type = request.form.get("user_type")
        
        # Validate username duplication
        data = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(data) != 0:
            return render_template("Register.html", error="Username already in use. Please try another one.", 
                                     CITIES=CITIES)
        
        # Validate email duplication
        data = db.execute("SELECT * FROM users WHERE email = ?", email)
        if len(data) != 0:
            return render_template("Register.html", error="Email Address is already in use. Please try another one.", 
                                     CITIES=CITIES)
        
        # Validate phone number duplication
        data = db.execute("SELECT * FROM users WHERE phone_number = ?", phone_number)
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
        if user_type == "doctor": # For doctors
            with open ("static/media/profile_picture.png", "rb") as pic:
                db.execute("INSERT INTO users (username, password_hash, full_name, city, phone_number, email, is_doctor, date_of_birth, profile_picture, is_verified) VALUES (?,?,?,?,?,?,TRUE,?,?,FALSE)",
                    username, password_hash, full_name, city, phone_number, email, date_of_birth, pic.read())
                session["user_type"] = "Doctor"
        else: # For patients
            with open ("static/media/profile_picture.png", "rb") as pic:
                db.execute("INSERT INTO users (username, password_hash, full_name, city, phone_number, email, is_doctor, date_of_birth, profile_picture, is_verified) VALUES (?,?,?,?,?,?,FALSE,?,?,FALSE)",
                    username, password_hash, full_name, city, phone_number, email, date_of_birth, pic.read())
                session["user_type"] = "Patient"
            
        # Session variables
        session["user_id"] = db.execute("SELECT * FROM users WHERE username = ?", username)[0]["id"]
        session["name"] = full_name
        
        # Redirect to home page
        return redirect("/")


@app.route("/Rigster/EmailVerify", methods=["GET", "POST"])
@login_required
def EmailVerify():
    global TEMP_CODE
    if request.method == "GET":
        email = db.execute("SELECT email FROM users WHERE id=?", session["user_id"])[0]["email"]
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(os.environ["EMAIL"], os.environ["PASSWORD"])
        TEMP_CODE = generate_random_number()
        server.sendmail(os.environ["EMAIL"], email, str(TEMP_CODE))
        server.close()
        return render_template("Email_Verification.html")

    else:
        user_code = request.form.get("code")
        if TEMP_CODE == int(user_code):
            db.execute("UPDATE users SET is_verified=1 WHERE id=?", session["user_id"])
            return redirect("/")
        else:
            return render_template("Email_Verification.html", error="Wrong code. New one was sent.")


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
        
        # Validate username
        data = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(data) != 1:
            return render_template("Login.html", error="Couldn't find user. Please try again.")
        
        # Validate password
        if not check_password_hash(data[0]["password_hash"], password):
            return render_template("Login.html", error="Wrong password. Please try again.")
        
        # Store the user id in the session's data
        session["user_id"] = data[0]["id"]
        session["name"] = data[0]["full_name"]
        if data[0]["is_doctor"]:
            session["user_type"] = "Doctor"
        else:
            session["user_type"] = "Patient"
        
        # Store the profile picture
        with open("static/media/profile_picture.png", "wb") as pic:
            profile_binary = db.execute("SELECT profile_picture FROM users WHERE id=?", session["user_id"])[0]["profile_picture"]
            pic.write(profile_binary)
            
        return redirect("/")
    

@app.route("/Logout")
@login_required
def logout():
    # Clear the existing session
    session.clear()
    
    # Delete profile picture
    if os.path.exists("static/media/profile_picture.png"):
        os.remove("static/media/profile_picture.png")

    # Redirect user to login form
    return redirect("/")


@app.route("/Settings")
@login_required
def settings():
    return render_template("settings.html")


@app.route("/Profile-<int:id>")
@login_required
def profile(id):
    data = db.execute("SELECT * FROM users WHERE id=?", id)
    return render_template("profile.html", data=data)


@app.route("/ChangePassword", methods=["GET", "POST"])
@login_required
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
@login_required
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
@login_required
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
@login_required
def edit_info():
    data = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])[0]
    if request.method == "GET":
        return render_template("edit_info.html", data=data, CITIES=CITIES)
    else:
        # Data input from the form
        username = request.form.get("username")
        full_name = request.form.get("full_name")
        phone_number = request.form.get("phone_number")
        city = request.form.get("city")
        date_of_birth = request.form.get("date_of_birth")
        profile_picture = request.files['profile_picture[]']
        
        # Validate username duplication and update db if valid
        if username:
            data_test = db.execute("SELECT * FROM users WHERE username = ? AND is_doctor = TRUE", username)
            if len(data_test) != 0:
                return render_template("edit_info.html", error1="Username already in use. Please try another one.", 
                                    data=data, CITIES=CITIES)
            db.execute("UPDATE users SET username=? WHERE id=?", username, session["user_id"])
        
        # Validate phone number duplication and update db if valid
        if phone_number:
            data_test = db.execute("SELECT * FROM users WHERE phone_number = ? AND is_doctor = TRUE", phone_number)
            if len(data_test) != 0:
                return render_template("edit_info.html", error2="Phone number is already in use. Please try another one.", 
                                    data=data, CITIES=CITIES)
            db.execute("UPDATE users SET phone_number=? WHERE id=?", phone_number, session["user_id"])
            
        # Validate user's age (older than 15) and update db if valid
        if date_of_birth:
            if Years_Between(date_of_birth, TODAY) < 15:
                return render_template("edit_info.html", error3="You have to be older than 15 years old to use", 
                                        data=data, CITIES=CITIES)
            db.execute("UPDATE users SET date_of_birth=? WHERE id=?", date_of_birth, session["user_id"])
        
        # Update data if edited
        if full_name:
            db.execute("UPDATE users SET full_name=? WHERE id=?", full_name, session["user_id"])
        if city:
            db.execute("UPDATE users SET city=? WHERE id=?", city, session["user_id"])
        
        # Store profile pic in static media
        profile_picture = request.files['profile_picture[]']
        if str(profile_picture) != "<FileStorage: '' ('application/octet-stream')>":
            profile_picture.save("static/media/profile_picture.png")
            with open ("static/media/profile_picture.png", "rb") as pic:
                db.execute("UPDATE users SET profile_picture=? WHERE id=?", pic.read(), session["user_id"])
                
        session["full_name"] = full_name
            
        # Redirect to home page
        return render_template("edit_info.html", data=data, CITIES=CITIES, success="Information updated successfully")


@app.route("/Patients")
@login_required
@doctors_only
def patients():
    patients = db.execute("SELECT * FROM users WHERE id=(SELECT patient_id FROM appointments WHERE doctor_id=?)", session["user_id"])
    return render_template("patients.html", patients=patients, Years_Between=Years_Between, TODAY=TODAY)


@app.route("/AccessDenied")
@login_required
def access_denied():
    return render_template("no_access.html")


# Error Handlers
@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(405)
@app.errorhandler(500)
@app.errorhandler(502)
def something_went_wrong(error):
   return render_template('went_wrong.html')