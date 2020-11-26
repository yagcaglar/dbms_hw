# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 15:54:35 2020

@author: Yağmur
"""

from flask import render_template, current_app,abort

def home_page():
    return render_template("home.html")

def profiles():
    db=current_app.config["db"]
    acms=db.get_all_accounts(0)
    return render_template("profiles.html", acms = sorted(acms))

def profile(user_type,user_name):
    db=current_app.config["db"]
    acm=db.get_account(user_type,user_name)
    if acm is None:
        abort(404)
    return render_template("profile.html", acm=acm)
