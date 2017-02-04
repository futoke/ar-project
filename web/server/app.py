#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
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

UPLOAD_FOLDER = 'static/models'
ALLOWED_EXTENSIONS = set(['fbx', 'obj', 'png', 'jpg', 'jpeg'])

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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def clear_dir(path):
    for the_file in os.listdir(path):
        file_path = os.path.join(path, the_file)

        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


@app.route('/upload/<model_name>/<action>', methods=['GET', 'POST'])
@login_required
def upload_file(model_name, action):
    if action != 'remove':
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)

            file = request.files['file']

            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    model_name,
                    action
                )

                if not os.path.exists(path):
                    os.makedirs(path)
                else:
                    clear_dir(path)

                file.save(os.path.join(path, filename))
                return ''
    else:
        pass
    return ''


@app.route('/download/<model_name>/<file_type>')
@login_required
def download_file(model_name, file_type):
    path = os.path.join(app.config['UPLOAD_FOLDER'], model_name, file_type)

    try:
        filename = os.listdir(path)[0]
        return send_from_directory(path, filename)
    except OSError:
        return ''

@app.route('/save_model/<model_id>', methods=['POST'])
@login_required
def save_model(model_id):
    print(model_id)
    data = request.get_json()

    with TinyDB('db.json') as db:
        print(db.get(Query().id == model_id))
        db.insert(data)

        # print(db.all())

    return ''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)