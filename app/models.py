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
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            postal_code INTEGER NOT NULL,
            occupation TEXT,
            register_date DATE NOT NULL,
            picture_path TEXT
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


def add_user(username, email, password_hash):
    # Insert a new user into the users table
    db.execute("INSERT INTO users (email, password_hash) VALUES (?, ?, ?)",
               username, email, password_hash)


def get_user_by_email(email):
    # Retrieve a user by email
    return db.execute("SELECT * FROM users WHERE email = ?", email)
