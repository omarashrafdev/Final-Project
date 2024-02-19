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
            full_name TEXT NOT NULL,
            gender TEXT NOT NULL,
            is_verified INTEGER NOT NULL DEFAULT 0,
            phone_number TEXT NOT NULL UNIQUE,
            city TEXT NOT NULL,
            date_of_birth DATE NOT NULL,
            picture_path TEXT
        );
    """)

    # Create patients table
    db.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            gender TEXT NOT NULL,
            date_of_birth DATE NOT NULL,
            phone_number TEXT NOT NULL,
            city TEXT NOT NULL,
            address TEXT,
            occupation TEXT,
            register_date DATE NOT NULL,
            picture_path TEXT,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)

    # Create patients documents table
    db.execute("""
        CREATE TABLE IF NOT EXISTS patient_docs (
            patient_id INTEGER PRIMARY KEY,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );
    """)

    # Create patients notes table
    db.execute("""
        CREATE TABLE IF NOT EXISTS patient_notes (
            patient_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            note TEXT NOT NULL,
            date DATE NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            PRIMARY KEY(patient_id, user_id) -- Added a composite primary key
        );
    """)

    # Create appointments table
    db.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            time TIME NOT NULL,
            treatment TEXT NOT NULL,
            description TEXT,
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


def get_user_by_phone_number(phone_number):
    return db.execute("SELECT * FROM users WHERE phone_number = ?", phone_number)


def add_user(email, password_hash, full_name, gender, phone_number, city, date_of_birth, picture_path=None):
    # Insert a new user into the users table
    db.execute("INSERT INTO users (email, password_hash, full_name, gender, phone_number, city, date_of_birth, picture_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
               email, password_hash, full_name, gender, phone_number, city, date_of_birth, picture_path)


# Patients CRUD
def add_patient(user_id, full_name, email, gender, date_of_birth, phone_number, city, address, occupation, picture_path=None):
    # Insert a new patient into the patients table
    db.execute("""
               INSERT INTO patients 
               (full_name, email, gender, date_of_birth, phone_number, city, address, occupation, picture_path, user_id, register_date) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               """,
               full_name, email, gender, date_of_birth, phone_number, city, address, occupation, picture_path, user_id, date.today())


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
def add_appointment(date, time, treatment, description, user_id, patient_id):
    # Insert a new appointment into the appointments table
    db.execute("INSERT INTO appointments (date, time, treatment, description, user_id, patient_id) VALUES (?, ?, ?, ?, ?, ?)",
               date, time, treatment, description, user_id, patient_id)


def get_appointments(user_id, patient_id):
    # Retrieve appointments for a specific user and patient
    return db.execute("SELECT * FROM appointments WHERE user_id=? AND patient_id=?", user_id, patient_id)


def update_appointment(appointment_id, date, time, treatment, description):
    # Update appointment details
    db.execute("UPDATE appointments SET date=?, time=?, treatment=?, description=? WHERE id=?",
               date, time, treatment, description, appointment_id)


def delete_appointment(appointment_id):
    # Delete appointment
    db.execute("DELETE FROM appointments WHERE id=?", appointment_id)


# Patient Docs CRUD
def add_patient_doc(patient_id, file_path, file_name):
    # Insert a new document for a patient into the patient_docs table
    db.execute("INSERT INTO patient_docs (patient_id, file_path, file_name) VALUES (?, ?, ?)",
               patient_id, file_path, file_name)


def get_patient_docs(patient_id):
    # Retrieve documents for a patient from the patient_docs table
    return db.execute("SELECT * FROM patient_docs WHERE patient_id=?", patient_id)


def delete_patient_doc(doc_id):
    # Delete a document from the patient_docs table
    db.execute("DELETE FROM patient_docs WHERE id=?", doc_id)


# Patient Notes CRUD
def add_patient_note(patient_id, user_id, note, date):
    # Insert a new note for a patient into the patient_notes table
    db.execute("INSERT INTO patient_notes (patient_id, user_id, note, date) VALUES (?, ?, ?, ?)",
               patient_id, user_id, note, date)


def get_patient_notes(patient_id):
    # Retrieve notes for a patient from the patient_notes table
    return db.execute("SELECT * FROM patient_notes WHERE patient_id=?", patient_id)
