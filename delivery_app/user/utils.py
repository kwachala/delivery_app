from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt
from . import flask_bcrypt


def hash_password(password):
    return flask_bcrypt.generate_password_hash(password).decode('utf-8')


def check_password_hash(hashed_password, plaintext_password):
    return flask_bcrypt.check_password_hash(hashed_password, plaintext_password)


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims['role'] != 'ADMIN':
            return jsonify(msg='Administration privileges required'), 403
        return fn(*args, **kwargs)

    return wrapper


def restauration_or_admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims['role'] != 'ADMIN' and claims['role'] != 'ADMIN':
            return jsonify(msg='Administration or restaurant privileges required'), 403
        return fn(*args, **kwargs)

    return wrapper
