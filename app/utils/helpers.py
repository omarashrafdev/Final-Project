from flask import session, redirect, url_for
from functools import wraps

# Example function to check if a user is logged in
def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function

# Other helper functions can be defined here
