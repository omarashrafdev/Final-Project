import re
from flask import redirect, session
from functools import wraps
from math import floor
from random import randint

def login_required(f):
    @wraps(f)
    def decorated_function1(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/Login")
        return f(*args, **kwargs)
    return decorated_function1

def doctors_only(f):
    @wraps(f)
    def decorated_function2(*args, **kwargs):
        if session.get("user_type") != "Doctor":
            return redirect("/AccessDenied")
        return f(*args, **kwargs)
    return decorated_function2

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

def minutes_between(date1, time1, date2, time2):
    date1 = str(date1)
    date2 = str(date2)
    days1 = int(date1.split("-")[0]*365) + (int(date1.split("-")[1])*30) + (int(date1.split("-")[2]))
    days2 = int(date2.split("-")[0]*365) + (int(date2.split("-")[1])*30) + (int(date2.split("-")[2]))
    print(days1-days2)#
    time1 = str(time1)
    time2 = str(time2)
    min1 = days1*24*60 + (int(time1.split(":")[0])*60) + int(time1.split(":")[1])
    min2 = days2*24*60 + (int(time2.split(":")[0])*60) + int(time2.split(":")[1])
    
    return (min1 - min2)

def generate_random_number():
    return randint(111111, 999999)

def swap(list, index1, index2):
    temp = list[index1]
    list[index1] = list[index2]
    list[index2] = temp