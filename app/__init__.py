from flask import Flask
from config import Config
from cs50 import SQL

# Initialize Flask application
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object(Config)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

# Import routes after initializing app to avoid circular imports
from app import routes