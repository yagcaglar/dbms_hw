from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import psycopg2
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
db_url=os.environ.get("DATABASE_URL")
con = psycopg2.connect(db_url, sslmode='require')
cur = con.cursor()

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

import routes
"""from datab import create_db

create_db()"""

