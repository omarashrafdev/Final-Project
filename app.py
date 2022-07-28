# Import needed functions
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from functions import login_required, strong_password_check

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded and enable debug mode
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.run(debug=True)

# Declare GLOBAL varable for the email verification function
#CODE = randint(000000, 999999)

# Store the URL generated with the secret key from the environment variable to the program
#s = URLSafeTimedSerializer(os.environ["SECRET_KEY"])

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

# Egyption's governorates list
GOVERNORATES = ["Alexandria", "Aswan", "Asyut", "Beheira", "Beni Suef", "Cairo", "Dakahlia", "Damietta", "Faiyum", "Gharbia", "Giza", "Ismailia", "Kafr El Sheikh", "Luxor", "Matruh", "Minya", "Monufia", "New Valley", "North Sinai", "Port Said", "Qalyubia ", "Qena", "Red Sea", "Sharqia", "Sohag", "South Sinai", "Suez"]

# Today's date to pass to the forms
#TODAY = date.today()

# Doctor Check (1=True, 0=False)
IS_DOCTOR = 0
# Email Verify Check (1=True, 0=False)
IS_VERIFIED = 0

@app.route("/")
@login_required
def index():
    # Essential variables
    #user_id = session["user_id"]
    
    # Return homapege view
    return render_template("index.html")


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

        data = db.execute("SELECT * FROM users WHERE username = ? AND is_doctor = TRUE", username)
        
        # Validate username
        if len(data) != 1:
            return render_template("Login.html", error="Couldn't find user. Please try again.")
        
        # Validate password
        if not check_password_hash(data[0]["password_hash"], password):
            return render_template("Login.html", error="Wrong password. Please try again.")
        
        session["user_id"] = data[0]["id"]
        '''
        with open("static/profile_pic.png", "wb") as pic:
            profile_binary = db.execute("SELECT profile_pic FROM users WHERE id=?", session["user_id"])[0]["profile_pic"]
            pic.write(profile_binary)'''
            
        return redirect("/")
    

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()
    
    # Delete profile picture
    '''
    if os.path.exists("static/profile_pic.png"):
        os.remove("static/profile_pic.png")'''

    # Redirect user to login form
    return redirect("/")