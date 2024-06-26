from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims['role'] != 'admin':
            return jsonify(msg='Administration privileges required'), 403
        return fn(*args, **kwargs)

    return wrapper


def restauration_or_admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims['role'] != 'admin' and claims['role'] != 'restaurant':
            return jsonify(msg='Administration or restaurant privileges required'), 403
        return fn(*args, **kwargs)

    return wrapper
