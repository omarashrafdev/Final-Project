from flask import Flask
from config import Config
from cs50 import SQL

# Initialize Flask application
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object(Config)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

from app import routes