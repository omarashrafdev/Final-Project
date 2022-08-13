import re
from flask import redirect, session
from functools import wraps
from math import floor
from random import randint

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/Login")
        return f(*args, **kwargs)
    return decorated_function

def doctors_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_type") != "Doctor":
            return redirect("/AccessDenied")
        return f(*args, **kwargs)
    return decorated_function

def strong_password_check(password):
    if(len(password) >= 8):
        if(bool(re.match('((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,30})', password)) == True):
            pass
        elif(bool(re.match('((\d*)([a-z]*)([A-Z]*)([!@#$%^&*]*).{8,30})', password)) == True):
            return 1
    else:
        return 2
    
def Years_Between(date1, date2):
    date1 = str(date1)
    date2 = str(date2)
    
    years1 = int(date1.split("-")[0]) + (int(date1.split("-")[1])/12) + (int(date1.split("-")[2])/365)
    years2 = int(date2.split("-")[0]) + (int(date2.split("-")[1])/12) + (int(date2.split("-")[2])/365)
    
    return floor(abs(years1 - years2))

def generate_random_number():
    return randint(111111, 999999)