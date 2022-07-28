from crypt import methods
import email
import os
import smtplib

from random import randint
from sre_constants import SUCCESS
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from functions import login_required, strong_password_check, Time_Between, Time_Convert, Years_Between


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded and enable debug mode
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.run(debug=True)

# Declare GLOBAL varable for the email verification function
CODE = randint(000000, 999999)

# Store the URL generated with the secret key from the environment variable to the program
s = URLSafeTimedSerializer(os.environ["SECRET_KEY"])

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

# Egyption's governorates list
GOVERNORATES = ["Alexandria", "Aswan", "Asyut", "Beheira", "Beni Suef", "Cairo", "Dakahlia", "Damietta", "Faiyum", "Gharbia", "Giza", "Ismailia", "Kafr El Sheikh", "Luxor", "Matruh", "Minya", "Monufia", "New Valley", "North Sinai", "Port Said", "Qalyubia ", "Qena", "Red Sea", "Sharqia", "Sohag", "South Sinai", "Suez"]

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
    global IS_DOCTOR
    global IS_VERIFIED
    
    # Setup Doctor variable for doctor view
    if db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]["is_doctor"] == True:
        IS_DOCTOR = 1
    else:
        IS_DOCTOR = 0

    # Verify Email if not verified
    if db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]["is_verified"] == True:
        IS_VERIFIED = 1
    else:
        IS_VERIFIED = 0
        return redirect("/Rigster/EmailVerify")
    
    # Get user's name
    name = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]["first_name"] + " " + db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]["last_name"]

    # Return homapege view
    return render_template("index.html", name = name, IS_DOCTOR = IS_DOCTOR)


@app.route("/Register", methods=["GET", "POST"])
def Register():
    # Clear the current session
    session.clear()

    if request.method == "GET":
        return render_template("Register.html", today=TODAY, governorates=GOVERNORATES)
    else:
        # Get username and password
        type = request.form.get("type")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        governorate = request.form.get("governorate")
        username = request.form.get("username")
        password = request.form.get("password1")
        date_of_birth = request.form.get("date_of_birth")
        
        if type == "doctor":
            # Validate username duplication
            data = db.execute("SELECT * FROM users WHERE username = ? AND is_doctor = TRUE", username)
            if len(data) != 0:
                return render_template("Register.html", error="Username already in use. Please try another one.", 
                                       today=TODAY, governorates=GOVERNORATES)
                
            # Validate email duplication
            data = db.execute("SELECT * FROM users WHERE email = ? AND is_doctor = TRUE", email)
            if len(data) != 0:
                return render_template("Register.html", error="Email Address already in use. Please try another one.", 
                                       today=TODAY, governorates=GOVERNORATES)
                
            # Validate phone number duplication
            data = db.execute("SELECT * FROM users WHERE phone_number = ? AND is_doctor = TRUE", phone_number)
            if len(data) != 0:
                return render_template("Register.html", error="Phone number already in use. Please try another one.", 
                                       today=TODAY, governorates=GOVERNORATES)
                
            # Validate user's age (older than 15)
            if Years_Between(date_of_birth, TODAY) < 15:
                return render_template("Register.html", error="You have to be older than 15 years old to use", 
                                       today=TODAY, governorates=GOVERNORATES)
            
            # Validate password match
            if request.form.get("password1") != request.form.get("password2"):
                return render_template("Register.html", error="Passwords don't match. Please try again.", 
                                       today=TODAY, governorates=GOVERNORATES)
        
            # Validate password strength
            if strong_password_check(password) == 1:
                return render_template("Register.html", error="Please choose a more secure password. It should be longer than 6 characters, unique to you and difficult for others to guess.", today=TODAY)
            elif strong_password_check(password) == 2:
                return render_template("Register.html", error="Your password must be at least 8 characters long. Please try another.", today=TODAY, governorates=GOVERNORATES)
            
            password_hash = generate_password_hash(password)
            
            profile_picture = request.files['files[]']
            profile_picture.save("static/profile_pic.png")
            
            # Store user's data in the database
            with open ("static/profile_pic.png", "rb") as pic:
                db.execute("INSERT INTO users (username, password_hash, first_name, last_name, governorate, email, phone_number, is_doctor, date_of_birth, profile_pic) VALUES (?,?,?,?,?,?,?,TRUE,?,?)",
                   username, password_hash, first_name, last_name, governorate, email, phone_number, date_of_birth, pic.read())
            
            session["user_id"] = db.execute("SELECT * FROM users WHERE username = ?", username)[0]["id"]
            return redirect("/")
            
        elif type == "patient":
            # Validate username duplication
            data = db.execute("SELECT * FROM users WHERE username = ? AND is_doctor = FALSE", username)
            if len(data) != 0:
                return render_template("Register.html", error="Username already in use. Please try another one.", 
                                       today=TODAY, governorates=GOVERNORATES)
                
            # Validate email duplication
            data = db.execute("SELECT * FROM users WHERE email = ? AND is_doctor = FALSE", email)
            if len(data) != 0:
                return render_template("Register.html", error="Email Address already in use. Please try another one.", 
                                       today=TODAY, governorates=GOVERNORATES)
                
            # Validate phone number duplication
            data = db.execute("SELECT * FROM users WHERE phone_number = ? AND is_doctor = FALSE", phone_number)
            if len(data) != 0:
                return render_template("Register.html", error="Phone number already in use. Please try another one.", 
                                       today=TODAY, governorates=GOVERNORATES)
            
            # Validate password match
            if request.form.get("password1") != request.form.get("password2"):
                return render_template("Register.html", error="Passwords don't match. Please try again.", 
                                       today=TODAY, governorates=GOVERNORATES)
        
            # Validate password strength
            if strong_password_check(password) == 1:
                return render_template("Register.html", error="Please choose a more secure password. It should be longer than 6 characters, unique to you and difficult for others to guess.", today=TODAY)
            elif strong_password_check(password) == 2:
                return render_template("Register.html", error="Your password must be at least 8 characters long. Please try another.", today=TODAY, governorates=GOVERNORATES)
            
            password_hash = generate_password_hash(password)
            
            profile_picture = request.files['files[]']
            profile_picture.save("static/profile_pic.png")
            
            # Store user's data in the database
            with open ("static/profile_pic.png", "rb") as pic:
                db.execute("INSERT INTO users (username, password_hash, first_name, last_name, governorate, email, phone_number, is_doctor, date_of_birth, profile_pic) VALUES (?,?,?,?,?,?,?,FALSE,?,?)",
                   username, password_hash, first_name, last_name, governorate, email, phone_number, date_of_birth, pic.read())
            session["user_id"] = db.execute("SELECT * FROM users WHERE username = ?", username)[0]["id"]
            return redirect("/")


@app.route("/Login", methods=["GET", "POST"])
def Login():
    # Clear the current session
    session.clear()

    if request.method == "GET":
        return render_template("Login.html")
    else:
        # Get username and password
        username = request.form.get("username")
        password = request.form.get("password")
        type = request.form.get("type")

        if type == "doctor":
            data = db.execute("SELECT * FROM users WHERE username = ? AND is_doctor = TRUE", username)
            
            # Validate username
            if len(data) != 1:
                return render_template("Login.html", error="Couldn't find user. Please try again.")
            
            # Validate password
            if not check_password_hash(data[0]["password_hash"], password):
                return render_template("Login.html", error="Wrong password. Please try again.")
            
            session["user_id"] = data[0]["id"]
            
            with open("static/profile_pic.png", "wb") as pic:
                profile_binary = db.execute("SELECT profile_pic FROM users WHERE id=?", session["user_id"])[0]["profile_pic"]
                pic.write(profile_binary)
                
            return redirect("/")
        
        elif type == "patient":
            data = db.execute("SELECT * FROM users WHERE username = ? AND is_doctor = FALSE", username)
            
            # Validate username
            if len(data) != 1:
                return render_template("Login.html", error="Couldn't find user. Please try again.")
            
            # Validate password
            if not check_password_hash(data[0]["password_hash"], password):
                return render_template("Login.html", error="Wrong password. Please try again.")
            
            session["user_id"] = data[0]["id"]
            
            with open("static/profile_pic.png", "wb") as pic:
                profile_binary = db.execute("SELECT profile_pic FROM users WHERE id=?", session["user_id"])[0]["profile_pic"]
                pic.write(profile_binary)
            
            return redirect("/")


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()
    
    # Delete profile picture
    if os.path.exists("static/profile_pic.png"):
        os.remove("static/profile_pic.png")

    # Redirect user to login form
    return redirect("/")


@login_required
@app.route("/AddAppointments", methods=["GET", "POST"])
def AddAppointments():
    if not IS_DOCTOR:
        return render_template("NoAccess.html")
    
    PATIENTS_List = db.execute("SELECT username FROM users WHERE is_doctor = False")
    PATIENTS = [None] * len(PATIENTS_List)
    for i in range(len(PATIENTS_List)):
        PATIENTS[i] = PATIENTS_List[i]["username"]
    if request.method == "GET":
        return render_template("Add_Appointments.html", patients = PATIENTS)
    else:
        date = request.form.get("date")
        time = request.form.get("time")
        patient_username = request.form.get("patient")
        fees = request.form.get("fees")
        description = request.form.get("description")

        patient_id = db.execute("SELECT id from users WHERE username = ?", patient_username)[0]["id"]
        
        appointments = db.execute("SELECT time from appointments WHERE doctor_id = ? AND date = ?", session["user_id"], date)
        
        for appointment in appointments:
            if Time_Between(appointment["time"], time) < 30:
                error = "You can't add an appointment on this day at " + time + ". Because There's another appointment at " + appointment["time"]
                return render_template("Add_Appointments.html", patients = PATIENTS, error = error)
        
        db.execute("INSERT INTO appointments (date, time, patient_id, doctor_id, fees, description) VALUES (?,?,?,?,?,?)",
                   date, time, patient_id, session["user_id"], fees, description)
        
        
        return render_template("Add_Appointments.html", patients = PATIENTS, success = "Appintment added")
        

#@app.route("/AddImage", methods=["GET", "POST"])
#def AddImage():
    if request.method == "GET":
        return render_template("Add_Image.html")
    else:
        profile_picture = request.files['files[]']
        profile_picture.save("static/profile_pic.png")
        
        # Add data to database
        with open ("static/profile_pic.png", "rb") as pic:
            db.execute("UPDATE users SET profile_pic=? WHERE id=?", pic.read(), session["user_id"])
        
        return redirect("/")
    

@app.route("/ViewAppointments")
def ViewAppointments():
    if not IS_DOCTOR:
        return render_template("NoAccess.html")
    
    Appointments = db.execute("SELECT * FROM appointments WHERE doctor_id=? ORDER BY date ASC", session["user_id"])
    
    for i in range(len(Appointments)):
        Appointments[i]['patient_id'] = db.execute("SELECT first_name FROM users WHERE id=?", Appointments[i]['patient_id'])[0]['first_name'] + " " + db.execute("SELECT last_name FROM users WHERE id=?", Appointments[i]['patient_id'])[0]['last_name']
        Appointments[i]['doctor_id'] = db.execute("SELECT first_name FROM users WHERE id=?", Appointments[i]['doctor_id'])[0]['first_name'] + " " + db.execute("SELECT last_name FROM users WHERE id=?", Appointments[i]['doctor_id'])[0]['last_name']

    
    return render_template("Appointments.html", Appointments=Appointments, Time_Convert=Time_Convert)



@login_required
@app.route("/ViewAppointments/<int:id>", methods=["POST"])
def ViewFullAppointments(id):
    return redirect("/ViewAppointments")


#@login_required
@app.route("/ViewAppointments/<int:id>/Edit", methods=["POST"])
def EditAppointments(id):
    return redirect("/ViewAppointments")


@login_required
@app.route("/ViewAppointments/<int:id>/Delete", methods=["POST"])
def DeleteAppointments(id):
    db.execute("DELETE FROM appointments WHERE id=?", id)
    return redirect("/ViewAppointments")


@login_required
@app.route("/Doctors")
def Doctors():
    Doctors = db.execute("SELECT * FROM users WHERE is_doctor=True")
    for i in range(len(Doctors)):
        name = "static/doctors/" + str(Doctors[i]["id"]) + ".png"
        id = Doctors[i]["id"]
        with open(name, "wb") as pic:
            profile_binary = db.execute("SELECT profile_pic FROM users WHERE id=?", id)[0]["profile_pic"]
            pic.write(profile_binary)
    return render_template("Doctors.html", Doctors=Doctors)


@login_required
@app.route("/Settings")
def Settings():
    is_verified = db.execute("SELECT is_verified FROM users WHERE id=?", session["user_id"])[0]["is_verified"]
    return render_template("Settings.html", is_verified=is_verified)

@login_required
@app.route("/Settings/ChangePassword", methods=["GET", "POST"])
def ChangePassword():
    user_id = session["user_id"]
    if request.method == "GET":
        return render_template("Change_Password.html")
    else:
        old_password = request.form.get("password1") 
        real_password = db.execute("SELECT password_hash FROM users WHERE id=?", user_id)[0]["password_hash"]
        
        if not check_password_hash(real_password, old_password):
            return render_template("Change_Password.html", error="Wrong password. Please try again.")
            
        if request.form.get("password3") != request.form.get("password2"):
            return render_template("Change_Password.html", error="Passwords don't match. Please try again.")
        
        password = request.form.get("password3")
        
        # Validate password strength
        if strong_password_check(password) == 1:
            return render_template("Change_Password.html", error="Please choose a more secure password. It should be longer than 6 characters, unique to you and difficult for others to guess.")
        elif strong_password_check(password) == 2:
            return render_template("Change_Password.html", error="Your password must be at least 8 characters long. Please try another.")
        
        password_hash = generate_password_hash(request.form.get("password3"))
        
        db.execute("UPDATE users SET password_hash=? WHERE id=?", password_hash, user_id)
        
        return render_template("Change_Password.html", success="Password changed successfully")


@login_required
@app.route("/Rigster/EmailVerify", methods=["GET", "POST"])
def EmailVerify():
    if request.method == "GET":
        email = db.execute("SELECT email FROM users WHERE id=?", session["user_id"])[0]["email"]
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(os.environ["EMAIL"], os.environ["PASSWORD"])
        server.sendmail(os.environ["EMAIL"], email, str(CODE))
        server.close()

        return render_template("Email_Verification.html")
    else:
        user_code = request.form.get("code")
        if CODE == int(user_code):
            db.execute("UPDATE users SET is_verified=1 WHERE id=?", session["user_id"])
            return redirect("/")
        else:
            return render_template("Email_Verification.html", error="Wrong code. New one was sent.")


@app.route("/ResetPassword", methods=["GET", "POST"])
def ResetPassword():
    if request.method == "GET":
        return render_template("Reset_Password.html")
    else:
        user_email = request.form.get("email")
        data = db.execute("SELECT * FROM users WHERE email=?", user_email)
        
        if len(data) == 0:
            return render_template("Reset_Password.html", error="Email not found. Please try again.")
        
        token = s.dumps(user_email, salt="email-confirm")
        
        link = "\n" + url_for('ConfirmEmail', token=token, _external=True)
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(os.environ["EMAIL"], os.environ["PASSWORD"])
        server.sendmail(os.environ["EMAIL"], "ibnhebesha@gmail.com", link)
        server.close()
        
        return render_template("Reset_Password.html", success="Reset link sent to your email")


@app.route("/ConfirmEmail/<token>")
def ConfirmEmail(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
        print(email)
    except SignatureExpired:
        return "<h1>The token is expired!</h1>"
    return redirect(url_for("ConfirmNewPassword", token=token, email=email))


@app.route("/ConfirmNewPassword/<token>/<email>", methods=["GET", "POST"])
def ConfirmNewPassword(token, email):
    if request.method == "GET":
        return render_template("Reset_Password_Token.html", token=token, email=email)
    
    else:
        if request.form.get("password1") != request.form.get("password2"):
            return render_template("Reset_Password_Token.html", error="Passwords must match")
        
        password = request.form.get("password1")
        
        # Validate password strength
        if strong_password_check(password) == 1:
            return render_template("Reset_Password_Token.html", error="Please choose a more secure password. It should be longer than 6 characters, unique to you and difficult for others to guess.")
        elif strong_password_check(password) == 2:
            return render_template("Reset_Password_Token.html", error="Your password must be at least 8 characters long. Please try another.")
        
        password_hash = generate_password_hash(password)
        db.execute("UPDATE users SET password_hash=? WHERE email=?", password_hash, email)
        return redirect("/Login")



# Birthday Check
# Arabic Version
# View appointment
# Edit appointment
# Dashboard
# Design