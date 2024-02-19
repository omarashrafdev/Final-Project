from hashlib import md5
import os
from random import randint
from flask import render_template, request, redirect, url_for, session
from app import app
from app.models import db, create_tables, add_user, get_user_by_email, get_user_by_phone_number
from werkzeug.security import generate_password_hash

from app.utils.helpers import login_required, user_login

# Create tables when the application starts
create_tables()


@login_required
@app.route('/')
def index():
    return render_template('index.html', name=session['full_name'], email=session['email'], picture=session['picture_path'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        login_email = request.form.get("login_email")
        login_password = request.form.get("login_password")

        if (user_login(login_email, login_password)):
            return redirect('/'), 200
        else:
            return render_template("login.html", error="Invalid credentials. Please try again."), 401


# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":
        # Retrieve form data
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        full_name = request.form.get("full_name")
        gender = request.form.get("gender")
        phone_number = request.form.get("phone_number")
        city = request.form.get("city")
        date_of_birth = request.form.get("date_of_birth")
        picture = request.files['picture_path']

        # Check if email already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return render_template("register.html", error="Email already exists. Please choose a different one.")

        # Check if phone number exists
        existing_user = get_user_by_phone_number(phone_number)
        if existing_user:
            return render_template("register.html", error="Phone number already exists. Please choose a different one.")

        # Check if passwords match
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")

        # Hash the password
        password_hash = generate_password_hash(password)

        # Store picture in the server
        hash_object = md5(str(randint(111111, 999999)).encode()).hexdigest()
        picture_path = "app/static/media/pictures/{}.png".format(hash_object)
        while os.path.exists(picture_path):
            hash_object = md5(
                str(randint(111111, 999999)).encode()).hexdigest()
            picture_path = "app/static/media/pictures/{}.png".format(
                hash_object)
        picture.save(picture_path)
        media_picture_path = '/'.join(picture_path.split('/')[3:])

        # Add user to the database
        add_user(email, password_hash, full_name, gender,
                 phone_number, city, date_of_birth, media_picture_path)

        return redirect(url_for("login"))


@app.route('/logout', methods=['GET'])
def logout():
    # Clear the user session data
    session.clear()

    # Redirect the user to the login page
    return redirect(url_for('login'))


@app.route('/patient-list')
def patient_list():
    # TODO: Get user id from session data
    user_id = 1
    patient_list = db.execute(
        "SELECT * FROM patients WHERE user_id=?", user_id)
    return render_template('patient_list.html', patient_list=patient_list)


@app.route('/users')
def users():
    users = db.execute("SELECT * FROM users")
    return render_template('users.html', users=users)

# Add more routes as needed
