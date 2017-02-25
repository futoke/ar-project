#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import os.path
import shutil
import json

from functools import wraps

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    abort,
    send_from_directory
)
from flask_triangle import Triangle
from werkzeug.utils import secure_filename

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from data_uri import DataURI


MODELS_FOLDER = 'models'
LOGIN = 'admin'
PASSWORD = 'admin'

# Create the application object.
app = Flask(__name__, static_folder='static')
Triangle(app)

# Config.
app.debug = True
app.secret_key = 'wMIz4UK3=m!4525,IS441cWFI2H12l2BP2=7R<1wUun,1KoQe23!]m2A)`|{2w5'

def erase_dir(path):
    filelist = [ f for f in os.listdir(path)]
    for f in filelist:
        os.remove(os.path.join(path, f))


# Login required decorator.
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


@app.route('/')
@login_required
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != LOGIN or request.form['password'] != PASSWORD:
            error = u'Неверный логин или пароль'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    return redirect(url_for('login'))


@app.route('/save_model/<model_id>', methods=['POST'])
@login_required
def save_model(model_id):
    model_path = os.path.join(app.static_folder, MODELS_FOLDER, model_id)

    with TinyDB('db.json', storage=CachingMiddleware(JSONStorage)) as db:
            if db.search(Query().id == model_id):
                data = request.get_json()
            else:
                return 'Cannot find a model with the id {}'.format(model_id)

            # Write zip file.
            if data['zipfile']['content'] != '':
                erase_dir(model_path)

                zipfile_path = os.path.join(model_path, data['zipfile']['name'])
                with open(zipfile_path, "wb") as fh:
                    uri = DataURI(data['zipfile']['content'])
                    fh.write(uri.data)

                data['zipfile']['content'] = ''

            db.update(data, Query().id == model_id)

    return ''


@app.route('/add_model', methods=['POST'])
@login_required
def add_model():
    data = request.get_json()
    new_model_path = os.path.join(app.static_folder, MODELS_FOLDER, data['id'])

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
        shutil.rmtree(os.path.join(app.static_folder, MODELS_FOLDER, model_id))

    return ''


@app.route('/load_model_file/<model_id>', methods=['POST'])
# @login_required
def get_model(model_id):
    if request.form['username'] == LOGIN or request.form['password'] == PASSWORD:
        with TinyDB('db.json', storage=CachingMiddleware(JSONStorage)) as db:
            if not db.search(Query().id == model_id):
                return 'Cannot find a model with the id {}'.format(model_id)

            data = db.get(Query().id == model_id)

            filepath = os.path.join(app.static_folder, MODELS_FOLDER, model_id)
            if os.path.isfile(os.path.join(filepath, data['zipfile']['name'])):
                return send_from_directory(
                    filepath,
                    data['zipfile']['name'],
                    as_attachment=True)
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
    app.run(host='0.0.0.0', port=8080, threaded=True)