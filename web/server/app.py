#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import json
from functools import wraps

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
    send_from_directory
)
from flask_triangle import Triangle
from werkzeug.utils import secure_filename

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware


UPLOAD_FOLDER = 'static/models'

# Create the application object.
app = Flask(__name__, static_path='/static')
Triangle(app)

# Config.
app.debug = True
app.secret_key = 'wMIz4UK3=m!4525,IS441cWFI2H12l2BP2=7R<1wUun,1KoQe23!]m2A)`|{2w5'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Login required decorator.
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


def del_content(data):
    data['preview']['content'] = ''
    data['texture']['content'] = ''
    data['mesh']['content'] = ''

    return data


# Add only new data
@app.route('/save_model/<model_id>', methods=['POST'])
@login_required
def save_model(model_id):
    client_data = request.get_json()

    with TinyDB('db.json', storage=CachingMiddleware(JSONStorage)) as db:
        server_data = db.get(Query().id == model_id)

        # Holy shit!!! Bad architecture...
        if client_data['preview']['content'] == '':
            client_data['preview']['content'] = server_data['preview']['content']

        if client_data['texture']['content'] == '':
            client_data['texture']['content'] = server_data['texture']['content']

        if client_data['mesh']['content'] == '':
            client_data['mesh']['content'] = server_data['mesh']['content']

        db.update(client_data, Query().id == model_id)

    return ''


@app.route('/add_model', methods=['POST'])
@login_required
def add_model():
    data = request.get_json()

    with TinyDB('db.json', storage=CachingMiddleware(JSONStorage)) as db:
        db.insert(data)

    return ''


@app.route('/remove_model/<model_id>', methods=['POST'])
@login_required
def remove_model(model_id):
    with TinyDB('db.json', storage=CachingMiddleware(JSONStorage)) as db:
        db.remove(Query().id == model_id)

    return ''


@app.route('/load_models', methods=['GET'])
@login_required
def load_models():
    with TinyDB('db.json', storage=CachingMiddleware(JSONStorage)) as db:
        data = db.all()

    # Return only names and preveiw!!!
    for i, _ in enumerate(data):
        del_content(data[i])

    return json.dumps(data)


@app.route('/load_model/<model_id>', methods=['GET'])
@login_required
def load_model(model_id):
    with TinyDB('db.json', storage=CachingMiddleware(JSONStorage)) as db:
        data = db.get(Query().id == model_id)

    return json.dumps(del_content(data))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)