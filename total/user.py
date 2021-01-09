from flask import current_app
from flask_login import UserMixin
from total import cur

class User(UserMixin):
    def __init__(self, username, password, user_id):
        self.user_id = user_id
        self.username = username
        self.password= password
        self.active = True
    
    def get_id(self):
        return self.user_id
    
    @property
    def is_active(self):
        return self.active

def get_user(username):
    sql = "select password, user_id from person where username = '%s'" % username
    cur.execute(sql)
    user_info = cur.fetchone()
    user = User(username, user_info[0], user_info[1])
    return user