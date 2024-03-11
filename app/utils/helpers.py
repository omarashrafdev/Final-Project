from flask import session, redirect, url_for
from functools import wraps
from werkzeug.security import check_password_hash

from app.models import get_user_by_email


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function


def user_login(email, password):
    user = get_user_by_email(email)
    if len(user) != 1:
        return False

    # Validate password
    if not check_password_hash(user[0]["password_hash"], password):
        return False

    session['user_id'] = user[0]['id']
    session['email'] = user[0]['email']
    session['full_name'] = user[0]['full_name']
    return True
