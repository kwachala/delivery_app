from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims["role"] != "ADMIN":
            return jsonify(msg="Administration privileges required"), 403
        return fn(*args, **kwargs)

    return wrapper


def restauration_or_admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims["role"] != "ADMIN" and claims["role"] != "restaurant":
            return jsonify(msg="Administration or restaurant privileges required"), 403
        return fn(*args, **kwargs)

    return wrapper


def serialize_order_item(item):
    return {
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "quantity": item.quantity
    }
