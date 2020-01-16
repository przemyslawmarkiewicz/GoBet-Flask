from app import app
from flask import render_template
from .models import LoginForm, RegisterForm

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
            return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form = form)

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        form.add_user()
        # return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form = form)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')