from flask import render_template, request, redirect, url_for
from app import app
from app.models import db, create_tables, add_user, get_user_by_email

# Create tables when the application starts
create_tables()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patient-list')
def index():
    return render_template('index.html')

@app.route('/appointments')
def index():
    return render_template('index.html')

@app.route('/users')
def users():
    users = db.execute("SELECT * FROM users")
    return render_template('users.html', users=users)

# Add more routes as needed
