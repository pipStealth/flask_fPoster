import sqlite3
import time
import math
import re
from flask import url_for

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print(f"Error reading from the database: {e}")
        return []

    def addPost(self, title, text, url, user):
        try:
            self.__cur.execute("SELECT COUNT(*) as `count` FROM posts WHERE url LIKE ?", (url,))
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("A post with this URL already exists")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, ?, ?)", (title, text, url, tm, user))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Error adding the post to the database: {e}")
            return False

        return True

    def getPost(self, alias):
        try:
            self.__cur.execute("SELECT title, text FROM posts WHERE url LIKE ? LIMIT 1", (alias,))
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print(f"Error getting the post from the database: {e}")

        return (False, False)
    
    def getUserByPost(self, url):
        try:
            self.__cur.execute("SELECT user_id FROM posts WHERE url = ? LIMIT 1", (url,))
            res = self.__cur.fetchone()
            if res:
                return res['user_id']
            print("Post not found")
        except sqlite3.Error as e:
            print(f"Error getting user from the database: {e}")
        return None

    def getPostsAnonce(self):
        try:
            self.__cur.execute("SELECT id, title, text, url FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print(f"Error getting posts from the database: {e}")

        return []

    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute("SELECT COUNT(*) as `count1` FROM users WHERE email LIKE ?", (email,))
            res1 = self.__cur.fetchone()
            self.__cur.execute("SELECT COUNT(*) as `count2` FROM users WHERE name LIKE ?", (name,))
            res2 = self.__cur.fetchone()
            if res1['count1'] > 0 or res2['count2'] > 0:
                print("A user with this email/name already exists")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Error adding the user to the database: {e}")
            return False

        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute("SELECT * FROM users WHERE id = ? LIMIT 1", (user_id,))
            res = self.__cur.fetchone()
            if res:
                return res
            print("User not found")
        except sqlite3.Error as e:
            print(f"Error getting user from the database: {e}")
        return None

    def getUserByEmail(self, email):
        try:
            self.__cur.execute("SELECT * FROM users WHERE email = ? LIMIT 1", (email,))
            res = self.__cur.fetchone()
            if res:
                return res
            print("User not found")
        except sqlite3.Error as e:
            print(f"Error getting user by email from the database: {e}")
        return None
    
    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False
        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute("UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Error updating avatar in the database: {e}")
            return False
        return True
    
    def updatePostText(self, post_id, additional_text):
        try:
            self.__cur.execute("UPDATE posts SET text = text || ? WHERE id = ?", (additional_text, post_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Error updating post text in the database: {e}")
            return False
        return True
