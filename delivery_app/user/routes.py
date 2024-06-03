import os
import jwt
import datetime
from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from . import db2
from .models import Restaurant, Menu, MenuItem
from .utils import admin_required

user_bp = Blueprint('user', __name__)


# temporary
@user_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', None)
    password = request.form.get('password', None)
    role = request.form.get('role', None)
    try:
        restaurant_id = request.form.get('restaurant_id', None)
    except:
        restaurant_id = None

    key = os.getenv("JWT_KEY")
    secret = os.getenv("JWT_SECRET")

    if not isinstance(secret, str):
        return jsonify({'message': 'JWT secret is not a string', 'key': key, 'secret': secret}), 500

    # if not key or not secret:
    #     return jsonify({'message': 'JWT key or secret not set'}), 500

    # Stara wersja
    # access_token = create_access_token(identity=username,
    #                                    additional_claims={'role': role, 'restaurant_id': restaurant_id})
    # Nowa wersja
    payload = {
        'iss': key,
        'role': role,
        'sub': username,
        'restaurant_id': restaurant_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    access_token = jwt.encode(payload, secret, algorithm='HS256')

    return jsonify(access_token=access_token)


@user_bp.route('/restaurants', methods=['GET', 'POST'])
@jwt_required()
def handle_restaurants():
    if request.method == 'POST':
        claims = get_jwt()
        if 'role' not in claims or claims['role'] != 'admin':
            return jsonify({'message': 'Administrative privileges required'}), 403

        name = request.form.get('name')
        address = request.form.get('address')
        if not name or not address:
            return jsonify({'message': 'Name and address are required'}), 400

        new_restaurant = Restaurant(name=name, address=address)
        db2.session.add(new_restaurant)
        db2.session.flush()

        new_menu = Menu(restaurant_id=new_restaurant.id)
        db2.session.add(new_menu)
        db2.session.commit()

        return jsonify({'message': 'Restaurant created successfully'}), 201

    restaurants = Restaurant.query.all()
    return jsonify([{'id': r.id, 'name': r.name, 'address': r.address} for r in restaurants])

# if __name__ == '__main__':
#     with restaurant_app.app_context():
#         db.create_all()
#
#     restaurant_app.run(debug=True)
