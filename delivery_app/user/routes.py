import os
import jwt
import datetime
from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from . import user_db
from .models import User
from .utils import admin_required

user_bp = Blueprint('user', __name__)


@user_bp.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', None)
    password = request.form.get('password', None)
    role = request.form.get('role', None)

    if not username or not password or not role:
        return jsonify({'message': 'Missing required parameters'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    user = User(username=username, password=password, role=role)
    user_db.session.add(user)
    user_db.session.commit()

    key = os.getenv("JWT_KEY")
    secret = os.getenv("JWT_SECRET")

    payload = {
        'iss': key,
        'user_id': user.id,
        'role': user.role.value,
        'sub': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    access_token = jwt.encode(payload, secret, algorithm='HS256')

    return jsonify({'message': 'User created successfully', 'access_token': access_token}), 200


@user_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', None)
    password = request.form.get('password', None)

    if not username or not password:
        return jsonify({'message': 'Missing required parameters'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        key = os.getenv("JWT_KEY")
        secret = os.getenv("JWT_SECRET")
        payload = {
            'iss': key,
            'user_id': user.id,
            'role': user.role.value,
            'sub': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        access_token = jwt.encode(payload, secret, algorithm='HS256')

        return jsonify({'message': 'Login successful', 'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


@user_bp.route('/users', methods=['GET'])
def handle_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'password': u._password, 'role': u.role.value} for u in users])
