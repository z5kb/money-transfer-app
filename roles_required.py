from functools import wraps
from flask_login import current_user
from werkzeug.utils import redirect

"""
The roles_required decorator allows us to only allow users with certain roles to
enter the page decorated with it.

The syntax is as follows:

@app.route("/home")
@roles_required(<tuple of the roles' names (strings)>)
def home():
    return "You are in the home page"
"""


def roles_required(roles_required_list):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for role in roles_required_list:
                if current_user.get_role() == role:
                    return func(*args, **kwargs)
            return redirect("/unauthorized")
        return wrapper
    return decorator
