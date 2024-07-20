from flask_login import UserMixin
from flask import url_for, send_from_directory

class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def getName(self):
        return self.__user['name'] if self.__user else "NoName"
    
    def getEmail(self):
        return self.__user['email'] if self.__user else "Without Email"
    
    def getAvatar(self, app):
        img = None
    
        if not self.__user['avatar']:
            try:
                # Assuming 'static' is your static folder
                img_path = app.root_path + url_for('static', filename='images/ava.png')
    
                with open(img_path, "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Error loading default avatar image:", e)
        else:
            img = self.__user['avatar']
    
        return img
    
    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext == "png" or ext == "PNG":
            return True
        return False