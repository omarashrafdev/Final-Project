from datetime import date
from cs50 import SQL

# Initialize SQLite database
db = SQL("sqlite:///database.db")


def create_tables():
    # Create users table
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL
        );
    """)

    # Create patients table
    db.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            date_of_birth DATE NOT NULL,
            register_date DATE NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)

    # Create appointments table
    db.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            time TIME NOT NULL,
            treatment TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );
    """)


# User CRUD
def get_user_by_email(email):
    # Retrieve a user by email
    return db.execute("SELECT * FROM users WHERE email = ?", email)


def add_user(email, password_hash, full_name):
    # Insert a new user into the users table
    db.execute("INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)",
               email, password_hash, full_name)


# Patients CRUD
def create_patient(full_name, email, date_of_birth, user_id):
    # Insert a new patient into the patients table
    db.execute("""
               INSERT INTO patients 
               (full_name, email, date_of_birth, register_date, user_id) 
               VALUES (?, ?, ?, ?, ?)
               """,
               full_name, email, date_of_birth, date.today(), user_id)


def get_patients(user_id):
    return db.execute("SELECT * FROM patients WHERE user_id = ? ORDER BY full_name", user_id)


def update_patient(user_id, patient_id, full_name, email, gender, date_of_birth, phone_number, city, address, occupation, picture_path=None):
    # Update the patient details
    db.execute("""
               UPDATE patients SET
               full_name=?, email=?, gender=?, date_of_birth=?, phone_number=?, city=?, address=?, occupation=?, picture_path=?, register_date=?
               WHERE id=? AND user_id=?
               """,
               full_name, email, gender, date_of_birth, phone_number, city, address, occupation, picture_path, date.today(), patient_id, user_id)


def delete_patient(user_id, patient_id):
    # Delete the patient record
    db.execute("DELETE FROM patients WHERE user_id=? AND id=?",
               user_id, patient_id)


# Appointments CRUD
def create_appointment(date, time, treatment, user_id, patient_id):
    # Insert a new appointment into the appointments table
    db.execute("INSERT INTO appointments (date, time, treatment, user_id, patient_id) VALUES (?, ?, ?, ?, ?)",
               date, time, treatment, user_id, patient_id)


def get_all_appointments(user_id):
    # Retrieve appointments for a specific user with patient names
    return db.execute("""
        SELECT appointments.*, patients.full_name
        FROM appointments
        JOIN patients ON appointments.patient_id = patients.id
        WHERE appointments.user_id=?
    """, user_id)


def get_appointments(user_id, patient_id):
    # Retrieve appointments for a specific user and patient
    return db.execute("SELECT * FROM appointments WHERE user_id=? AND patient_id=?", user_id, patient_id)


def update_appointment(appointment_id, date, time, treatment):
    # Update appointment details
    db.execute("UPDATE appointments SET date=?, time=?, treatment=? WHERE id=?",
               date, time, treatment, appointment_id)


def delete_appointment(user_id, appointment_id):
    # Delete appointment
    db.execute("DELETE FROM appointments WHERE id=? AND user_id=?",
               appointment_id, user_id)
