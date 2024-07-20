import sqlite3
import os
from flask import Flask, make_response, render_template, request, g, flash, abort, redirect, url_for
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from admin.admin import admin

# конфигурация
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'main.db')))

app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "You need sign in to site for read this page!"
login_manager.login_message_category = "error"
MAX_CONTENT_AVATAR = 1024 * 1024
the_name = None

@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.errorhandler(401)
def notlogin(error):
    return render_template("page401.html"), 401

@app.errorhandler(404)
def page_not_found(error):
    return render_template("page404.html"), 404


@app.route("/")
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce(), title="Home page")

@app.route("/add_post", methods=["POST", "GET"])
@login_required
def addPost():

    if request.method == "POST":
    
        res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'], current_user.get_id()) 
        flash('Error from DB(Flask)', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title="Add post")


@app.route("/post/<alias>")
@login_required
def showPost(alias):
    user_id = dbase.getUserByPost(alias)
    if not user_id:
        abort(404)
    
    user = dbase.getUser(user_id)
    if not user:
        abort(404)
    
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)
    
    return render_template('post.html', 
                           menu=dbase.getMenu(), 
                           title=title, 
                           post=post, 
                           user_id=user_id, 
                           name=user['name'], 
                           ava=user["avatar"])


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("The password or login not correct", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Authorization")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
            and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2'] \
            and "@" in request.form["email"] and "." in request.form["email"]:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Success! You are welcome!", "success")
                return redirect(url_for('login'))
            else:
                flash("DB Error(Flask)", "error")
        else:
            flash("The name/email/psw so short(min 4) or psw1 ≠ psw2 or email is not correct", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Registration")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Success! You log out from account!", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", menu=dbase.getMenu(), title="Profile")

@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""
    
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h

@app.route('/avatar/<int:user_id>')
@login_required
def uAva(user_id):
    user = dbase.getUser(user_id)
    if not user:
        abort(404)

    img = user["avatar"]
    if not img:
        return ""
    
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h
        
@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files.get('file')
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Error update: Avatar.", "error")
                flash("Success!", "success")
            except FileExistsError as e:
                flash("Warnging from DB(Flask - the file can't read)", "error")
        else:
            flash("This type of files is unsupported or too large for server.", "error")
    return redirect(url_for("profile"))


if __name__ == "__main__":
    app.run(debug=True)