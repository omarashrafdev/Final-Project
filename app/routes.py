from hashlib import md5
import os
from random import randint
from flask import render_template, request, redirect, url_for, session
from app import app
from app.models import *
from werkzeug.security import generate_password_hash

from app.utils.helpers import login_required, user_login

# Create tables when the application starts
create_tables()


@login_required
@app.route('/')
def index():
    if 'full_name' in session:
        return render_template('index.html', name=session['full_name'], email=session['email'])
    else:
        return redirect('/login')


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

        # Check if email already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return render_template("register.html", error="Email already exists. Please choose a different one.")

        # Check if passwords match
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")

        # Hash the password
        password_hash = generate_password_hash(password)

        # Add user to the database
        add_user(email, password_hash, full_name)

        return redirect("/login")


@app.route('/logout', methods=['GET'])
def logout():
    # Clear the user session data
    session.clear()

    # Redirect the user to the login page
    return redirect("/login")


@app.route('/patients')
def patients():
    if 'full_name' in session:
        patients = get_patients(session['user_id'])
        return render_template('patients.html', patients=patients, name=session['full_name'])
    else:
        return redirect('/login')


@app.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    if 'full_name' in session:
        if request.method == "GET":
            return render_template('add_patient.html', name=session['full_name'])
        else:
            full_name = request.form.get("full_name")
            email = request.form.get("email")
            date_of_birth = request.form.get("date_of_birth")

            create_patient(full_name, email, date_of_birth, session['user_id'])

            return redirect('/patients')
    else:
        return redirect('/login')


@app.route('/patients/delete', methods=['POST'])
def remove_patient():
    if 'full_name' in session:
        patient_id = request.form.get("id")
        delete_patient(session['user_id'], patient_id)
        return redirect('/patients')
    else:
        return redirect('/login')


@app.route('/appointments')
def appointments():
    if 'full_name' in session:
        appointments = get_all_appointments(session['user_id'])
        return render_template('appointments.html', appointments=appointments, name=session['full_name'])
    else:
        return redirect('/login')


@app.route('/appointments/add', methods=['GET', 'POST'])
def add_appointment():
    if 'full_name' in session:
        patients = get_patients(session['user_id'])
        if request.method == "GET":
            return render_template('add_appointment.html', patients=patients, name=session['full_name'])
        else:
            try:
                treatment = request.form.get("treatment")
                date = request.form.get("date")
                time = request.form.get("time")
                patient_id = request.form.get("patient_id")
                create_appointment(date, time, treatment,
                                   session['user_id'], patient_id)
                return redirect('/appointments')
            except Exception as e:
                print(e)  # Print the exception for debugging
                return render_template('add_appointment.html', patients=patients, error="An error occurred. Please try again.")
    else:
        return redirect('/login')
