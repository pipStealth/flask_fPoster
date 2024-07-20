from flask import Blueprint, Flask, g, redirect, request, session, render_template, url_for, flash
import sqlite3

admin = Blueprint('admin', __name__, template_folder="templates", static_folder="static")

db = None

@admin.before_request
def before_request():
    global db
    db = g.get('link_db')

@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request

menu = [{'url': '.index', 'title': 'Panel'},
        {'url': '.listpub', 'title': "List of lines"},
        {'url': '.listusers', 'title': 'List of users'},
        {'url': '.logout', 'title': 'Logout'}]

def login_admin():
    session['admin_logged'] = 1

def isLogged():
    return True if session.get('admin_logged') else False 

def logout_admin():
    session.pop('admin_logged', None)

def redirect_delete():
    return redirect(url_for('.delete_account'))

@admin.route('/', methods=['GET', 'POST'])
def index():
    if not isLogged():
        return redirect(url_for('admin.login'))
        
    return render_template('admin/index.html', menu=menu, title='Админ-панель')

@admin.route('/login', methods=["POST", "GET"])
def login():
    if isLogged():
        return redirect(url_for('admin.index'))
    if request.method == 'POST':
        if request.form['user'] == 'admin' and request.form['psw'] == '123':
            login_admin()
            return redirect(url_for('admin.index'))
        else:
            flash("Not correct login/password", "error")
    
    return render_template("admin/login.html", title="Adminlogin")

@admin.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('admin.login'))
    
    logout_admin()

    return redirect(url_for('admin.login'))


@admin.route('/listpubs')
def listpub():
    if not isLogged():
        return redirect(url_for('.login'))
    
    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT title, text, url FROM posts")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print(e)
    
    return render_template('admin/listpubs.html', title="[A] List line", menu=menu, list=list)

@admin.route('/listusers')
def listusers():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT name, email FROM users ORDER BY time DESC")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения статей из БД " + str(e))

    return render_template('admin/listusers.html', title='[A] List of user', menu=menu, list=list)

@admin.route('/delpost', methods=["POST", "GET"])
def dela():
    if not isLogged():
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        try:
            cur = db.cursor()
            url_pattern = request.form['url']
            
            # SQL query with LIKE and %
            cur.execute("DELETE FROM posts WHERE url LIKE ?", ('%' + url_pattern + '%',))
            db.commit()

            flash("Posts deleted successfully", "success")
        except sqlite3.Error as e:
            print("Error deleting posts from the database: " + str(e))
            flash("Error deleting posts", "error")

    return render_template("admin/dela.html", title="Delete Posts", menu=menu)

@admin.route('/delete_account', methods=["POST", "GET"])
def delete_account():
    if not isLogged():
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        try:
            cur = db.cursor()
            email_pattern = request.form.get('email', '')
            
            # SQL query with LIKE and %
            cur.execute("DELETE FROM users WHERE email LIKE ?", ('%' + email_pattern + '%',))
            db.commit()

            flash("Email deleted successfully", "success")
        except sqlite3.Error as e:
            print("Error deleting emails from the database: " + str(e))
            flash("Error deleting emails", "error")

    return render_template("admin/delete.html", title="Delete Emails", menu=menu)