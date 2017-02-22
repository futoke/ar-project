#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import os.path
import shutil
import json
import base64
from functools import wraps

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    abort,
    flash,
    send_from_directory
)
from flask_triangle import Triangle
from werkzeug.utils import secure_filename

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from data_uri import DataURI


UPLOAD_FOLDER = 'static/models'

# Create the application object.
app = Flask(__name__, static_folder='static/models')
Triangle(app)

# Config.
app.debug = True
app.secret_key = 'wMIz4UK3=m!4525,IS441cWFI2H12l2BP2=7R<1wUun,1KoQe23!]m2A)`|{2w5'


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


@app.route('/save_model/<model_id>', methods=['POST'])
@login_required
def save_model(model_id):
    model_path = os.path.join(UPLOAD_FOLDER, model_id)

    with TinyDB('db.json', storage=CachingMiddleware(JSONStorage)) as db:
            if db.search(Query().id == model_id):
                data = request.get_json()
            else:
                return 'Cannot find a model with the id {}'.format(model_id)

            # Write zip file.
            if data['zipfile']['content'] != '':
                zipfile_path = os.path.join(model_path, data['zipfile']['name'])
                with open(zipfile_path, "wb") as fh:
                    uri = DataURI(data['zipfile']['content'])
                    fh.write(uri.data)

                data['zipfile']['content'] = ''

            # Write preview image.
            if data['preview']['content'] != '':
                zipfile_path = os.path.join(model_path, data['preview']['name'])
                with open(zipfile_path, "wb") as fh:
                    uri = DataURI(data['preview']['content'])
                    fh.write(uri.data)

                data['preview']['content'] = ''

            db.update(data, Query().id == model_id)

    return ''


@app.route('/add_model', methods=['POST'])
@login_required
def add_model():
    data = request.get_json()
    new_model_path = os.path.join(UPLOAD_FOLDER, data['id'])

    if not os.path.exists(new_model_path):
        os.makedirs(new_model_path)

    with TinyDB('db.json', storage=CachingMiddleware(JSONStorage)) as db:
        db.insert(data)

    return ''


@app.route('/remove_model/<model_id>', methods=['POST'])
@login_required
def remove_model(model_id):
    with TinyDB('db.json', storage=CachingMiddleware(JSONStorage)) as db:
        if not db.search(Query().id == model_id):
            return 'Cannot find a model with the id {}'.format(model_id)

        db.remove(Query().id == model_id)
        shutil.rmtree(os.path.join(UPLOAD_FOLDER, model_id))

    return ''


@app.route('/load_model_file/<model_id>/<filetype>', methods=['GET'])
@login_required
def get_model(model_id, filetype):
    with TinyDB('db.json', storage=CachingMiddleware(JSONStorage)) as db:
        if not db.search(Query().id == model_id):
            return 'Cannot find a model with the id {}'.format(model_id)

        data = db.get(Query().id == model_id)
        if filetype in ('zipfile', 'preview'):
            filepath = os.path.join(app.static_folder, model_id)
            return send_from_directory(filepath, data[filetype]['name'])
        else:
            abort(404)

    return ''


@app.route('/load_models', methods=['GET'])
@login_required
def load_models():
    with TinyDB('db.json', storage=CachingMiddleware(JSONStorage)) as db:
        data = db.all()

    return json.dumps(data)


@app.route('/load_model/<model_id>', methods=['GET'])
@login_required
def load_model(model_id):
    with TinyDB('db.json', storage=CachingMiddleware(JSONStorage)) as db:
        if not db.search(Query().id == model_id):
            return 'Cannot find a model with the id {}'.format(model_id)
        data = db.get(Query().id == model_id)

    return json.dumps(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)