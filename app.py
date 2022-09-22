# Import needed libraries
from crypt import methods
import os
import time
import imghdr
import traceback
from turtle import pos

# Import needed functions
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from cs50 import SQL
from datetime import date
from werkzeug.security import check_password_hash, generate_password_hash
from hashlib import md5
from functions import *

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded and enable debug mode
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.run(debug=True)

# Declare GLOBAL varable for the email verification function
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
CITIES = [
    "Alexandria", 
    "Aswan", 
    "Asyut", 
    "Beheira", 
    "Beni Suef", 
    "Cairo", 
    "Dakahlia", 
    "Damietta", 
    "Faiyum", 
    "Gharbia", 
    "Giza", 
    "Ismailia", 
    "Kafr El Sheikh", 
    "Luxor", 
    "Matruh", 
    "Minya", 
    "Monufia", 
    "New Valley", 
    "North Sinai", 
    "Port Said", 
    "Qalyubia ", 
    "Qena", 
    "Red Sea", 
    "Sharqia", 
    "Sohag", 
    "South Sinai", 
    "Suez"
]

# Today's date to pass to the forms
TODAY = date.today()
TIME = time.ctime(time.time()).split(" ")[4][:-3]


@app.route("/", methods=["GET"])
@login_required
def index():
    # Return homapege view
    return render_template("index.html")


@app.route("/Register", methods=["GET", "POST"])
def Register():
    # Clear the current session
    session.clear()

    if request.method == "GET":
        return render_template("register.html",  CITIES=CITIES)
    else:
        # Data input from the form
        username = request.form.get("username")
        name = request.form.get("name")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        gender = request.form.get("gender")
        city = request.form.get("city")
        birthday = request.form.get("birthday")
        picture = request.files['picture[]']

        # Validate username duplication
        data = db.execute("SELECT * FROM user_login WHERE username = ?", username)
        if len(data) != 0:
            return render_template("register.html", error="Username already in use\nPlease try another one", CITIES=CITIES)

        # Validate name format
        # TODO

        # Validate email duplication
        data = db.execute("SELECT * FROM users WHERE email = ?", email)
        if len(data) != 0:
            return render_template("register.html", error="Email Address is already in use\nPlease try another one", CITIES=CITIES)

        # Validate phone number duplication
        data = db.execute("SELECT * FROM users WHERE phone_number = ?", phone_number)
        if len(data) != 0:
            return render_template("register.html", error="Phone number is already in use\nPlease try another one", CITIES=CITIES)

        # Validate gender
        if gender not in ["male", "female"]:
            return render_template("register.html", error="Non existing gender selected\nPlease try again", CITIES=CITIES)

        # Validate city
        if city not in CITIES:
            return render_template("register.html", error="Non existing city selected\nPlease try again", CITIES=CITIES)

        # Validate user's age (older than 18)
        if Years_Between(birthday, TODAY) < 18:
            return render_template("register.html", error="You have to be older than 18 years old to use", CITIES=CITIES)

        # Validate image
        if imghdr.what(picture) not in ["jpg", "jpeg", "png"]:
            return render_template("register.html", error="Image file type is not supported\nOnly (jpg, jpeg, png) files are supported", CITIES=CITIES)

        # Validate password match
        if request.form.get("password1") != request.form.get("password2"):
            return render_template("register.html", error="Passwords don't match. Please try again.", CITIES=CITIES)

        # Validate password strength
        password = request.form.get("password1")
        if strong_password_check(password) == 1:
            return render_template("register.html", error="Please choose a more secure password. It should be longer than 6 characters, unique to you and difficult for others to guess.", CITIES=CITIES)
        elif strong_password_check(password) == 2:
            return render_template("register.html", error="Your password must be at least 8 characters long. Please try another.", CITIES=CITIES)
        password_hash = generate_password_hash(password)

        # Store picture in the server
        hash_object = md5(str(generate_random_number()).encode()).hexdigest()
        picture_path = "static/media/pictures/{}.png".format(hash_object)
        while os.path.exists(picture_path):
            hash_object = md5(str(generate_random_number()).encode()).hexdigest()
            picture_path = "static/media/pictures/{}.png".format(hash_object)
        picture.save(picture_path)

        # Store user's data in the database
        db.execute("Insert INTO users (name, gender, email, phone_number, city, birthday, picture_path) VALUES (?,?,?,?,?,?,?)",
                name, gender, email, phone_number, city, birthday, picture_path)
        
        # Session variables
        session["user_id"] = db.execute("SELECT id FROM users WHERE email = ?", email)[0]["id"]
        session["username"] = username
        session["name"] = name
        session["picture_path"] = picture_path
        session["is_verified"] = "False"

        # Store user's login data in the database
        db.execute("INSERT INTO user_login (user_id, username, password_hash) VALUES (?,?,?)", session["user_id"], username, password_hash)
        
        # Redirect to home page
        return redirect("/Rigster/EmailVerify")


@app.route("/Rigster/EmailVerify", methods=["GET"])
@login_required
def EmailVerify():
    global TEMP_CODE
    if request.method == "GET":
        # Get email from DB
        email = db.execute("SELECT email FROM users WHERE id=?", session["user_id"])[0]["email"]

        # Sent a code to the email
        TEMP_CODE = generate_random_number()
        subject = "[CliMan] Please verify your account"
        content = "Hey {}\n\nYou recently created an account on CLIMAN but to use your account you need to verify.\nEnter the verification code on your account to proceed\n\nVerification code: {}\n\nThanks,\nThe CLIMAN Team".format(session["username"], TEMP_CODE)
        sene_mail(email, subject, content)
        
        return redirect("/Rigster/EmailVerify/Code")


@app.route("/Rigster/EmailVerify/Code", methods=["GET", "POST"])
@login_required
def EmailCode():
    if request.method == "GET":
        return render_template("email_verification.html")
    else:
        user_code = request.form.get("code")
        if TEMP_CODE == int(user_code):
            db.execute("UPDATE users SET is_verified=1 WHERE id=?", session["user_id"])
            session["is_verified"] = "True"
            return redirect("/")
        else:
            return render_template("email_verification.html", error="Wrong code. Please try again")


@app.route("/Login", methods=["GET", "POST"])
def login():
    # Clear the current session
    session.clear()

    if request.method == "GET":
        return render_template("login.html")
    else:
        # Get username and password
        username = request.form.get("username")
        password = request.form.get("password")

        # Validate username
        data = db.execute("SELECT * FROM user_login WHERE username = ?", username)
        if len(data) != 1:
            return render_template("login.html", error="Couldn't find user. Please try again.")

        # Validate password
        if not check_password_hash(data[0]["password_hash"], password):
            return render_template("login.html", error="Wrong password. Please try again.")

        # Store the user id in the session's data
        user_data = db.execute("SELECT * FROM users WHERE id=?", data[0]["user_id"])

        session["user_id"] = user_data[0]["id"]
        session["username"] = data[0]["username"]
        session["name"] = user_data[0]["name"]
        session["picture_path"] = user_data[0]["picture_path"]
        if user_data[0]["is_verified"] == 1:
            session["verified"] = "True"
        else:
            session["verified"] = "False"
        
        return redirect("/")


@app.route("/Logout")
@login_required
def logout():
    # Clear the existing session
    session.clear()

    # Redirect user to login form
    return redirect("/")


# Patient Section
@app.route("/Patients", methods=["GET", "POST"])
@login_required
def patients():
    # patients_id = db.execute("SELECT * FROM user_patients WHERE user_id=?", session["user_id"])
    # patients = db.execute("SELECT * FROM patients WHERE id=?", patients_id)
    # appointments = db.execute("SELECT * FROM WHERE")
    '''
    for patient in patients:
        # list of appointments for this patient
        appointments = db.execute(
            "SELECT * FROM appointments WHERE doctor_id=? AND patient_id=? ORDER BY date", session["user_id"], patient["id"])

        next_appointment_date = appointments[0]["date"]
        next_appointment_time = appointments[0]["time"]

        for i in range(len(appointments)):
            if minutes_between(appointments[i]["date"], appointments[i]["time"], next_appointment_date, next_appointment_time) > 0:
                if minutes_between(appointments[i]["date"], appointments[i]["time"], str(TODAY), str(TIME)) > 0:
                    next_appointment_date = appointments[i]["date"]
                    next_appointment_time = appointments[i]["time"]
                    patient['next_appointment'] = appointments[i]["date"] + \
                        " " + appointments[i]["time"]
                    break
                else:
                    patient['last_appointment'] = appointments[i]["date"] + \
                        " " + appointments[i]["time"]
            else:
                patient['last_appointment'] = appointments[i]["date"] + \
                    " " + appointments[i]["time"]

        if next_appointment_date == appointments[0]["date"] and next_appointment_time == appointments[0]["time"] and minutes_between(next_appointment_date, next_appointment_time, str(TODAY), str(TIME)) < 0:
            patient['next_appointment'] = "-"

    for i in range(len(patients)):
        name = "static/media/patients/" + str(patients[i]["id"]) + ".png"
        id = patients[i]["id"]
        with open(name, "wb") as pic:
            profile_binary = db.execute("SELECT profile_picture FROM users WHERE id=?", id)[
                0]["profile_picture"]
            pic.write(profile_binary)
    '''
    if request.method == "GET":
        return render_template("patients.html", selected="name")

    else:
        sort_by = request.form.get("sort_by")
        if sort_by == "name":
            return render_template("patients.html", patients=patients, selected="name")

        elif sort_by == "next_appointment":
            # Sorting by next_appointment
            sorted_patients = patients.copy()
            length = len(sorted_patients)

            # Sorting patients who doesn't have appointment to the end of the list
            counter1 = length-1
            for i in range(length-1, -1, -1):
                if sorted_patients[i]["next_appointment"] == "-":
                    # Move to the bottom of the list
                    swap(sorted_patients, i, counter1)
                    counter1 -= 1

            # Sorting patients who have an appointment from latest to earlier
            swap_counter = -1
            j = 0
            while swap_counter != 0:
                swap_counter = 0
                for i in range(0, counter1-j):
                    if minutes_between(
                            sorted_patients[i]["next_appointment"].split(" ")[0],
                            sorted_patients[i]["next_appointment"].split(" ")[1],
                            sorted_patients[i+1]["next_appointment"].split(" ")[0],
                            sorted_patients[i+1]["next_appointment"].split(" ")[1]) > 0:
                        swap(sorted_patients, i, i+1)
                        swap_counter += 1
                j += 1

            return render_template("patients.html", patients=sorted_patients, selected="next_appointment")

        elif sort_by == "last_appointment":
            print("Sorting by: "+sort_by)
            # Sorting by last_appointment
            sorted_patients = patients.copy()
            length = len(sorted_patients)

            # Sorting patients who doesn't have appointment to the end of the list
            counter1 = length-1
            for i in range(length-1, -1, -1):
                if sorted_patients[i]["last_appointment"] == "-":
                    # Move to the bottom of the list
                    swap(sorted_patients, i, counter1)
                    counter1 -= 1

            # Sorting patients who have an appointment from latest to earlier
            swap_counter = -1
            j = 0
            while swap_counter != 0:
                swap_counter = 0
                for i in range(0, counter1-j):
                    if minutes_between(
                            sorted_patients[i]["last_appointment"].split(" ")[0],
                            sorted_patients[i]["last_appointment"].split(" ")[1],
                            sorted_patients[i+1]["last_appointment"].split(" ")[0],
                            sorted_patients[i+1]["last_appointment"].split(" ")[1]) < 0:
                        swap(sorted_patients, i, i+1)
                        swap_counter += 1
                j += 1

            return render_template("patients.html", patients=sorted_patients, selected="last_appointment")


@app.route("/Patients/Profile-<int:id>")
@login_required
def patient_profile(id):
    user_data = db.execute("SELECT * FROM users WHERE id=?", id)[0]
    user_data["address"] = "El-badr st, 21"
    user_data["zip"] = 32154
    user_data["register_date"] = "2004-12-4"
    user_data["status"] = "Active"
    return render_template("patient_profile.html", patient=user_data)


@app.route("/Patients/Delete-<int:id>")
@login_required
def delete_patient(id):
    db.execute("DELETE FROM appointments WHERE doctor_id=? AND patient_id=?",session["user_id"], id)
    return redirect("/Patients")


@app.route("/AddPatient", methods=["GET", "POST"])
@login_required
def add_patient():
    if request.method == "GET":
        return render_template("add_patient.html", CITIES=CITIES)
    else:
        print("Begin")
        # Data input from the form
        name = request.form.get("name")
        email = request.form.get("email")
        gender = request.form.get("gender")
        birthday = request.form.get("birthday")
        phone_number = request.form.get("phone_number")
        address = request.form.get("address")
        city = request.form.get("city")
        postal_code = request.form.get("postal_code")
        occupation = request.form.get("occupation")
        print("Before Passed")
        picture = request.files['picture']
        print("Passed")
        

        # Validate name format
        # TODO

        # Validate email duplication
        data = db.execute("SELECT * FROM patients WHERE email = ?", email)
        if len(data) != 0:
            return render_template("add_patient.html", error="Email Address is already in use\nPlease try another one", CITIES=CITIES)
        print("Passed")
        # Validate phone number duplication
        data = db.execute("SELECT * FROM patients WHERE phone_number = ?", phone_number)
        if len(data) != 0:
            return render_template("add_patient.html", error="Phone number is already in use\nPlease try another one", CITIES=CITIES)
        print("Passed")
        # Validate gender
        if gender not in ["male", "female"]:
            return render_template("add_patient.html", error="Non existing gender selected\nPlease try again", CITIES=CITIES)
        print("Passed")
        # Validate city
        if city not in CITIES:
            return render_template("add_patient.html", error="Non existing city selected\nPlease try again", CITIES=CITIES)
        print("Passed")
        # Validate ZIP
        if len(postal_code) != 5:
            return render_template("add_patient.html", error="Invalid postal code\nPlease try again", CITIES=CITIES)
        print("Passed")
        # Validate image
        if imghdr.what(picture) not in ["jpg", "jpeg", "png"]:
            return render_template("add_patient.html", error="Image file type is not supported\nOnly (jpg, jpeg, png) files are supported", CITIES=CITIES)
        print("Passed")
        # Store picture in the server
        hash_object = md5(str(generate_random_number()).encode()).hexdigest()
        picture_path = "static/media/pictures/{}.png".format(hash_object)
        while os.path.exists(picture_path):
            hash_object = md5(str(generate_random_number()).encode()).hexdigest()
            picture_path = "static/media/pictures/{}.png".format(hash_object)
        picture.save(picture_path)

        # Store user's data in the database
        db.execute("Insert INTO patients (name, email, gender, birthday, phone_number, address, city, postal_code, occupation, register_date, picture_path) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                name, email, gender, birthday, phone_number, address, city, postal_code, occupation, TODAY, picture_path)
        
        return render_template("add_patient.html", error="Success", CITIES=CITIES)



@app.route("/AddAppointment", methods=["GET", "POST"])
@login_required
def add_appointment():
    if request.method == "GET":
        return render_template("add_appointment.html")
    else:
        date = request.form.get("date")
        time = request.form.get("time")
        patient_id = request.form.get("patient")
        fees = request.form.get("fees")
        description = request.form.get("description")

        appointments = db.execute("SELECT time, date from appointments WHERE doctor_id = ? AND date = ?", session["user_id"], date)
        
        for appointment in appointments:
            if abs(minutes_between(date, time, appointment["date"], appointment["time"])) < 30:
                error = "You can't add an appointment on this day at " + time + ". Because There's another appointment at " + appointment["time"]
                return render_template("add_appointment.html", patients = patients, error = error)

        db.execute("INSERT INTO appointments (date, time, patient_id, doctor_id, fees, description) VALUES (?,?,?,?,?,?)",
                   date, time, patient_id, session["user_id"], fees, description)

        return redirect("/Patients")
# End of Patient Section


# Settings Section
@app.route("/Settings")
@login_required
def settings():
    return render_template("settings.html")


@app.route("/ChangePassword", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "GET":
        return render_template("change_password.html")
    else:
        # Get old password from the user
        old_password = request.form.get("old_password")

        data = db.execute("SELECT password_hash FROM user_login WHERE user_id = ?", session["user_id"])
        # Validate current password
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
        db.execute("UPDATE user_login SET password_hash=? WHERE user_id=?", password_hash, session["user_id"])

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

        # TODO - Token
        # The message
        TEMP_CODE = generate_random_number()
        message = "\nThis is your code: " + str(TEMP_CODE)

        # Sent a code to the email
        TEMP_CODE = generate_random_number()
        subject = "[CliMan] Please verify your email"
        content = "Hey {}\n\nYou recently requested to change your email for account on CLIMAN. Please verify this email.\nEnter the verification code on your account to proceed\n\nVerification code: {}\n\nThanks,\nThe CLIMAN Team".format(session["username"], TEMP_CODE)
        sene_mail(email, subject, content)

        # Redirect to the verify function to verify the new email with the code
        return redirect(url_for("verify_new_email", email=email))


# TODO - Bug _Custom email passed through url_
@app.route("/VerifyNewEmail/<email>", methods=["GET", "POST"])
@login_required
def verify_new_email(email):
    if request.method == "GET":
        return render_template("verify_new_email.html", email=email)
    else:
        # Get the code the user has entered
        code = int(request.form.get("code"))

        # Validate code
        if code != TEMP_CODE:
            return render_template("verify_new_email.html", error="Wrong code. Please try again.", email=email)

        # Update the email in the database
        db.execute("UPDATE users SET email=? WHERE id=?", email, session["user_id"])

        # Redirect to home page
        return redirect("/")


@app.route("/EditInfo", methods=["GET", "POST"])
@login_required
def edit_info():
    data = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])[0]
    data["username"] = db.execute("SELECT username FROM user_login WHERE user_id=?", session["user_id"])[0]["username"]
    if request.method == "GET":
        print(session["picture_path"])
        return render_template("edit_info.html", data=data, CITIES=CITIES)
    else:
        Edited = False

        # Data input from the form
        username = request.form.get("username")
        name = request.form.get("name")
        phone_number = request.form.get("phone_number")
        city = request.form.get("city")
        birthday = request.form.get("birthday")
        picture = request.files['profile_picture[]']

        # Validate username duplication and update db if valid
        if username:
            data_test = db.execute("SELECT * FROM user_login WHERE username=?", username)
            if len(data_test) != 0:
                return render_template("edit_info.html", error1="Username already in use. Please try another one.", data=data, CITIES=CITIES)
            db.execute("UPDATE user_login SET username=? WHERE user_id=?", username, session["user_id"])
            session["username"] = username
            data["username"] = username
            Edited = True

        # Validate phone number duplication and update db if valid
        if phone_number:
            data_test = db.execute("SELECT * FROM users WHERE phone_number=?", phone_number)
            if len(data_test) != 0:
                return render_template("edit_info.html", error2="Phone number is already in use. Please try another one.", data=data, CITIES=CITIES)
            db.execute("UPDATE users SET phone_number=? WHERE id=?", phone_number, session["user_id"])
            data["phone_number"] = phone_number
            Edited = True

        # Validate user's age (older than 15) and update db if valid
        if birthday:
            if Years_Between(birthday, TODAY) < 15:
                return render_template("edit_info.html", error3="You have to be older than 15 years old to use", data=data, CITIES=CITIES)
            db.execute("UPDATE users SET birthday=? WHERE id=?", birthday, session["user_id"])
            data["birthday"] = birthday
            Edited = True

        # Update data if edited
        if name:
            db.execute("UPDATE users SET name=? WHERE id=?", name, session["user_id"])
            session["name"] = name
            data["birthday"] = birthday
            Edited = True
        if city:
            db.execute("UPDATE users SET city=? WHERE id=?", city, session["user_id"])
            data["city"] = city
            Edited = True

        # Update profile pic
        if str(picture) != "<FileStorage: '' ('application/octet-stream')>":
            # Deleting current image
            if os.path.exists(session["picture_path"]):
                os.remove(session["picture_path"])
            
            # Storing new image
            hash_object = md5(str(generate_random_number()).encode()).hexdigest()
            picture_path = "static/media/pictures/{}.png".format(hash_object)
            while os.path.exists(picture_path):
                hash_object = md5(str(generate_random_number()).encode()).hexdigest()
                picture_path = "static/media/pictures/{}.png".format(hash_object)
            picture.save(picture_path)
            db.execute("UPDATE users SET picture_path=? WHERE id=?", picture_path, session["user_id"])
            session["picture_path"] = picture_path
            Edited = True

        # Redirect to home page
        if Edited:
            return render_template("edit_info.html", data=data, CITIES=CITIES, success="Information updated successfully")
        else:
            return render_template("edit_info.html", data=data, CITIES=CITIES)
# End of Settings Section


# Help Section
@app.route("/Help", methods=["GET", "POST"])
@login_required
def help():
    if request.method == "GET":
        return render_template("help.html")
    else:
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        subject = "[CliMan] Report from {} - {}".format(session["username"], subject)
        content = "Name: {}\nEmail: {}\n\nMessage: {}".format(name, email, message)

        # Send message to the new email
        sene_mail(os.environ["EMAIL"], subject, content)

        return render_template("thank_you.html")
# End of Help Section


# Profile Section
@app.route("/Profile-<int:id>")
@login_required
def profile(id):
    data = db.execute("SELECT * FROM users WHERE id=?", id)
    return render_template("profile.html", data=data)
# End of Profile Section


# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    code = str(e)[0:3]
    return render_template('404.html', code=code)


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(405)
@app.errorhandler(500)
@app.errorhandler(502)
def something_went_wrong(e):
    code = str(e)[0:3]
    return render_template('went_wrong.html', code=code)
# End of Error Handlers