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
    # try:
    #     restaurant_id = request.form.get('restaurant_id', None)
    # except:
    #     restaurant_id = None

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
    # role = request.form.get('role', None)
    # try:
    #     restaurant_id = request.form.get('restaurant_id', None)
    # except:
    #     restaurant_id = None

    if not username or not password:
        return jsonify({'message': 'Missing required parameters'}), 400

    user = User.query.filter_by(username=username).first()

    key = os.getenv("JWT_KEY")
    secret = os.getenv("JWT_SECRET")

    # if not isinstance(secret, str):
    #     return jsonify({'message': 'JWT secret is not a string', 'key': key, 'secret': secret}), 500

    # if not key or not secret:
    #     return jsonify({'message': 'JWT key or secret not set'}), 500

    # Stara wersja
    # access_token = create_access_token(identity=username,
    #                                    additional_claims={'role': role, 'restaurant_id': restaurant_id})
    # Nowa wersja

    if user and user.check_password(password):
        payload = {
            'iss': key,
            'role': user.role.value,
            'sub': username,
            # 'restaurant_id': restaurant_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        access_token = jwt.encode(payload, secret, algorithm='HS256')
        # access_token = create_access_token(identity={'username': user.username, 'role': user.role.name},
        #                                    expires_delta=timedelta(hours=1))
        # return jsonify(access_token=access_token)
        return jsonify({'message': 'Login successful', 'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


@user_bp.route('/users', methods=['GET'])
def handle_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'password': u._password, 'role': u.role.value} for u in users])

# if __name__ == '__main__':
#     with restaurant_app.app_context():
#         db.create_all()
#
#     restaurant_app.run(debug=True)
