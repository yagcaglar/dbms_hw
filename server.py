# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 15:57:38 2020

@author: Yağmur
"""

from flask import Flask
import view
from database import Database

def create_app():
    app=Flask(__name__)
    
    app.add_url_rule("/", view_func=view.home_page)
    app.add_url_rule("/profiles", view_func=view.profiles)
    app.add_url_rule("/profiles/<int:user_type><user_name>", view_func=view.profile
    
    db=Database()
    app.config["db"]= db
    
    return app

if __name__ == "__main__":
    app= create_app()
    app.run(host="0.0.0.0", port=8080, debug=True)
    