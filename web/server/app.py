# -*- coding:utf-8 -*-

from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps

# Create the application object.
app = Flask(__name__, static_path='/static')

# Config.
app.debug = True
app.secret_key = 'wMIz4UK3=m!4525,IS441cWFI2H12l2BP2=7R<1wUun,1KoQe23!]m2A)`|{2w5'


# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/')
@login_required
def home():
    return render_template('index.html')


@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = u'Неверный логин или пароль'
        else:
            session['logged_in'] = True
            flash('You were logged in.')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('welcome'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)