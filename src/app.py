# This file is part of OneTimeFileSharing 
#
# Copyright (C) 2024 Charudatta
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
from flask import Flask, request, send_file, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os
import uuid
from flask_migrate import Migrate
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.String(36), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #upload_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    #deadline = db.Column(db.DateTime, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/test')
def test_connection():
    logger.info("Test connection endpoint was accessed")
    return "connected"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"New user registered: {username}")
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            logger.info(f"User logged in: {username}")
            return redirect(url_for('upload_file'))
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logger.info(f"User logged out: {current_user.username}")
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            logger.error("No file part in the request")
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            logger.error("No selected file")
            return 'No selected file', 400
        if file:
            file_id = str(uuid.uuid4())
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
            key = get_random_bytes(16)
            cipher = AES.new(key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(file.read())
            with open(file_path, 'wb') as f:
                [f.write(x) for x in (cipher.nonce, tag, ciphertext)]
            logger.info(f"File uploaded: {file.filename} by user: {current_user.username}")
            return {'file_id': file_id, 'key': key.hex()}, 201
    return render_template('upload.html')

@app.route('/download/<file_id>/<key>', methods=['GET'])
def download_file(file_id, key):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            nonce, tag, ciphertext = [f.read(x) for x in (16, 16, -1)]
        cipher = AES.new(bytes.fromhex(key), AES.MODE_EAX, nonce=nonce)
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            os.remove(file_path)
            logger.info(f"File downloaded: {file_id} by user: {current_user.username}")
            return send_file(io.BytesIO(plaintext), attachment_filename='downloaded_file', as_attachment=True)
        except ValueError:
            logger.error("Key incorrect or message corrupted")
            return 'Key incorrect or message corrupted', 400
    else:
        logger.error(f"File not found: {file_id}")
        return 'File not found', 404   
 
@app.route('/')
def index():
    return redirect(url_for('login'))

def add_admin():
    with app.app_context():
        db.metadata.create_all(db.engine)
        if User.query.all():
            create = input('A user already exists! Create another? (y/n):')
            if create == 'y':
                username = input('Enter username: ')
                password = input('Enter password: ')
                assert password == input('Enter password again: ')
                user = User(
                    username=username, 
                    password=generate_password_hash(password, method='pbkdf2:sha256'))
                db.session.add(user)
                db.session.commit()


if __name__ == '__main__':
    #add_admin()
    app.run(debug=True)


