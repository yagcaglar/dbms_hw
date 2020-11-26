# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 19:10:12 2020

@author: Yağmur
"""
class Account:
    def __init__(self,name,surname,user_type,user_name):
        self.name=name
        self.surname=surname
        self.user_type=user_type
        self.user_name=user_name

class Database:
    def __init__(self):
        self.acm_accounts={}
        self.user_accounts={}
        self.acm_number=0
        self.user_number=0
    
    def add_user(self,user):
        if user.type==0: 
            self.acm_accounts[self.acm_number]=user
            self.acm_number+=1
        else:
            self.user_accounts[self.user_number]=user
            self.user_number+=1
            
    def delete_account(self,user_type,user_name):
        if user_type==0:
            if user_name in self.acm_accounts:
                del self.acm_accounts[user_name]
        else:
            if user_name in self.user_accounts:
                del self.user_accounts[user_name]
                
    def get_account(self,user_type,user_name):
        if user_type==0:
            user=self.acm_accounts.get(user_name)
        else:
            user=self.user_accounts.get(user_name)
        if user is None:
            return None
        account=Account(user.name,user.surname,user_type,user_name)
        return account
    
    def get_all_accounts(self,user_type):
        if user_type == 0:
            acms=[]
            
            for index, acm in self.acm_accounts.items():
                acm_=Account(acm.name,acm.surname,acm.user_type,acm.user_name)
                acms.append((index,acm_))
            return acms
        else: 
            users=[]
            for index, user in self.user_accounts.items():
                user_=Account(user.name,user.surname,user.user_type,user.user_name)
                users.append((index,user_))
                
            return users