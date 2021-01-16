from flask import current_app
from flask_login import UserMixin
from server import cur

class User(UserMixin):
    def __init__(self, user_id, username, password, acm):
        self.user_id = user_id
        self.username = username
        self.password= password
        self.acm = acm
        self.active = True
    
    def get_id(self):
        return self.username
    
    @property
    def is_active(self):
        return self.active


def get_user(username):
    sql = "SELECT user_id,username,password, is_acm from person where username = '{}'".format(username)
    cur.execute(sql)
    info = cur.fetchone()
    if info is not None:
        user = User(info[0],info[1],info[2],info[3])
        return user
    else:
        return None