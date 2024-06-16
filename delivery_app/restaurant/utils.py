from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt
import jwt


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
        if claims["role"] != "ADMIN" and claims["role"] != "RESTAURANT":
            return jsonify(msg="Administration or restaurant privileges required"), 403
        return fn(*args, **kwargs)

    return wrapper


def serialize_restaurant_menu(menu):
    return {
        "items": [
            {"id": item.id, "name": item.name, "price": item.price}
            for item in menu.items
        ]
    }


def get_jwt_claims_unverified():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    token = auth_header.split(" ")[1]
    try:
        claims = jwt.decode(token, options={"verify_signature": False})
        return claims
    except jwt.InvalidTokenError:
        return None