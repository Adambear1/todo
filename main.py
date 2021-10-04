from datetime import datetime
import os

from peewee import DoesNotExist, ProgrammingError, IntegrityError
from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import pbkdf2_sha256

from model import Task, User

app = Flask(__name__)
app.secret_key = b'\x9d\xb1u\x08%\xe0\xd0p\x9bEL\xf8JC\xa3\xf4J(hAh\xa4\xcdw\x12S*,u\xec\xb8\xb8'


@app.route('/all', methods=['GET'])
def all_tasks():
    '''
    All:
        -   GET:
                - Renders all.jinja2 template
    '''
    if request.method == "GET":
        error = session["error"] if "error" in session else ""
        return render_template('all.jinja2', tasks=Task().select(), error=error)


@app.route('/create', methods=['GET', 'POST'])
def create():
    '''
    Create:
        -   GET:
                - If user is logged in, then render create.jinja2 template
                - If no user, then redirects to login template
        -   POST:
                - Reads form request submitted. If no task name, then reprompts user for updated field.
                - Task is saved, if no errors, redirected to 'all' page.
    '''
    error = session["error"] if "error" in session else ""
    if request.method == "GET":
        if 'username' not in session:
            session['error'] = "Please login or signup firsts to continue!"
            return redirect(url_for('login'))
        return render_template("create.jinja2", error=error)
    if request.method == "POST":
        if not request.form["name"]:
            return render_template("create.jinja2", error="The name request is required to be filled to continue!")
        performed = datetime.now() if "performed" in request.form else None
        performed_by = User().get(
            username=session["username"]) if performed else None
        task = Task().create(
            name=request.form["name"], performed=performed, performed_by=performed_by)
        if task:
            session["error"] = ""
            return redirect(url_for("all_tasks"))
        return render_template("create.jinja2", error="System Error Saving Input")


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Login:
        -   GET:
                - Renders login.jinja2 template
        -   POST:
                - Reads form request submitted. Validates user exists and passwords matched.
                - If not user, then redirected to signup page.
                - If incorrect password, then prompted to login again.
                - Else, new session is stored with updated username.
    '''
    try:
        error = session["error"] if "error" in session else ""
        if request.method == "GET":
            return render_template('login.jinja2', error=error)
        if request.method == 'POST':
            user = User.select().where(
                User.username == request.form['username']).get()
            if user and pbkdf2_sha256.verify(request.form['password'], user.password):
                session['username'] = request.form['username']
                session['error'] = ""
                return redirect(url_for('all_tasks'))
            return render_template('login.jinja2', error="Incorrect password!")
    except DoesNotExist:
        session["error"] = "User does not exist. Try signing up."
        return redirect(url_for("signup"))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    '''
    Signup:
        -   GET:
                - Renders signup.jinja2 template
        -   POST:
                - Reads form request submitted. Validates user is unique and password is present.
                - If user, then redirected to login page.
                - If no password, then prompted to signup again.
                - Else, user is created and redirected to 'all' page.
    '''
    try:
        if request.method == "GET":
            error = session["error"] if "error" in session else ""
            return render_template("signup.jinja2", error=error)
        if request.method == 'POST':
            if "username" not in request.form or "password" not in request.form:
                return render_template("signup", error="Make sure both username and password are present!")
            User(username=request.form['username'], password=pbkdf2_sha256.hash(
                request.form['password'])).save()
            session["username"] = request.form["username"]
            session["error"] = None
            return redirect(url_for('all_tasks'))
    except IntegrityError:
        session["username"] = ""
        session["error"] = "{} already exists!".format(
            request.form['username'])
        return redirect(url_for("login"))


@app.route('/incomplete', methods=['GET', 'POST'])
def incomplete_tasks():
    '''
    Incomplete:
        -   GET:
                - If user is logged in, then renders all incomplete tasks. Else redirect to login template.
                - If no incomplete tasks, then returns user to all template.
        -   POST:
                - Able to update (complete) tasks.
    '''
    tasks = Task().select().where(Task.performed.is_null())
    if request.method == "GET":
        if 'username' not in session:
            session['error'] = "Please login to continue!"
            return redirect(url_for('login'))
        if len(tasks) == 0:
            session['error'] = "All tasks are complete!"
            return redirect(url_for("all_tasks"))
        return render_template("incomplete.jinja2", tasks=tasks, error=session["error"] if "error" in session else '')
    if request.method == 'POST':
        user = User.select().where(User.username == session['username']).get()
        Task.update(performed=datetime.now(), performed_by=user).where(
            Task.id == request.form['task_id']).execute()
        session['error'] = ""
        return redirect(url_for("incomplete_tasks"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port)
