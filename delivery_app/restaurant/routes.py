import json
import random
from kombu import Connection, Exchange, Queue

from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from . import db
from .models import Restaurant, Menu, MenuItem
from .utils import admin_required

restaurant_bp = Blueprint('restaurant', __name__)

broker_url = 'pyamqp://guest:guest@rabbitmq:5672//'
connection = Connection(broker_url)
orders_exchange = Exchange('orders', type='direct')
orders_queue = Queue('orders_queue', exchange=orders_exchange, routing_key='orders')


@restaurant_bp.route('/restaurant/register', methods=['POST'])
@jwt_required()
def register_restaurant():
    claims = get_jwt()

    owner_id = claims['user_id']

    name = request.form.get('name', None)
    address = request.form.get('address', None)
    cuisine = request.form.get('cuisine', None)

    if claims['role'] == 'CUSTOMER' or claims['role'] == 'DELIVERER':
        return jsonify({'message': 'Insufficient permission'}), 403

    if not name or not address or not cuisine:
        return jsonify({'message': 'Missing required parameters'}), 400

    if Restaurant.query.filter_by(name=name).first():
        return jsonify({'message': 'Restaurant with given name already exists'}), 400

    restaurant = Restaurant(name=name, address=address, cuisine=cuisine, status='pending', owner_id=owner_id)
    db.session.add(restaurant)
    db.session.commit()

    return jsonify({'message': 'Restaurant registration submitted. Awaiting approval.'}), 201


@restaurant_bp.route('/restaurant/approve/<int:restaurant_id>', methods=['POST'])
@jwt_required()
def approve_restaurant(restaurant_id):
    claims = get_jwt()

    if not claims or claims['role'] != 'ADMIN':
        return jsonify({'message': 'Administrative privileges required'}), 403

    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return jsonify({'message': 'Restaurant not found'}), 404

    restaurant.status = 'active'
    db.session.commit()

    return jsonify({'message': 'Restaurant approved'}), 200


@restaurant_bp.route('/restaurant/reject/<int:restaurant_id>', methods=['POST'])
@jwt_required()
def reject_restaurant(restaurant_id):
    claims = get_jwt()

    if not claims or claims['role'] != 'ADMIN':
        return jsonify({'message': 'Administrative privileges required'}), 403

    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return jsonify({'message': 'Restaurant not found'}), 404

    restaurant.status = 'inactive'
    db.session.commit()

    return jsonify({'message': 'Restaurant rejected'}), 200


@restaurant_bp.route('/restaurant/status/<int:restaurant_id>', methods=['GET'])
@jwt_required()
def restaurant_status(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)
    claims = get_jwt()
    if not claims or (claims['role'] != 'ADMIN' and claims['user_id'] != restaurant.owner_id):
        return jsonify({'message': 'Only the owner or an admin can perform this action'}), 403

    if not restaurant:
        return jsonify({'message': 'Restaurant not found'}), 404

    return jsonify({'id': restaurant.id, 'status': restaurant.status}), 200


@restaurant_bp.route('/restaurants/pending', methods=['GET'])
@jwt_required()
def pending_restaurants():
    claims = get_jwt()

    if not claims or claims['role'] != 'ADMIN':
        return jsonify({'message': 'Administrative privileges required'}), 403

    restaurants = Restaurant.query.filter_by(status='pending').all()
    return jsonify([{'id': r.id, 'name': r.name, 'address': r.address, 'cuisine': r.cuisine, 'status': r.status,
                     'owner_id': r.owner_id} for r in restaurants])


@restaurant_bp.route('/restaurants', methods=['GET'])
@jwt_required()
def handle_restaurants():
    restaurants = Restaurant.query.all()

    return jsonify([{'id': r.id, 'name': r.name, 'address': r.address, 'cuisine': r.cuisine, 'status': r.status,
                     'owner_id': r.owner_id} for r in restaurants])


@restaurant_bp.route('/restaurant/<int:restaurant_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_restaurant(restaurant_id):
    claims = get_jwt()
    restaurant = Restaurant.query.get(restaurant_id)

    if request.method in ['PUT', 'DELETE']:
        if claims['role'] != 'ADMIN' and restaurant.owner_id != claims['user_id']:
            return jsonify({'message': 'Only the owner or an admin can perform this action'}), 403

    if not restaurant:
        return jsonify({'message': 'Restaurant not found'}), 404

    if request.method == 'GET':
        return get_restaurant_status(restaurant)
    elif request.method == 'PUT':
        return update_restaurant(restaurant)
    elif request.method == 'DELETE':
        return delete_restaurant(restaurant)


def get_restaurant_status(restaurant):
    return jsonify(
        {'id': restaurant.id, 'name': restaurant.name, 'address': restaurant.address, 'cuisine': restaurant.cuisine,
         'status': restaurant.status, 'owner_id': restaurant.owner_id}), 200


def update_restaurant(restaurant):
    name = request.form.get('name', None)
    address = request.form.get('address', None)
    cuisine = request.form.get('cuisine', None)

    if name:
        restaurant.name = name
    if address:
        restaurant.address = address
    if cuisine:
        restaurant.cuisine = cuisine

    db.session.commit()
    return jsonify([{'message': 'Restaurant details updated successfully'},
                    {'id': restaurant.id, 'name': restaurant.name, 'address': restaurant.address,
                     'cuisine': restaurant.cuisine,
                     'status': restaurant.status, 'owner_id': restaurant.owner_id}]), 200


def delete_restaurant(restaurant):
    db.session.delete(restaurant)
    db.session.commit()
    return jsonify({'message': 'Restaurant deleted successfully'}), 200


# @restaurant_bp.route('/menu/<int:menu_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
# @jwt_required()
# def handle_menu(menu_id):
#     claims = get_jwt()
#     menu = Menu.query.get_or_404(menu_id)
#     user_restaurant_id = claims['restaurant_id']
#
#     if request.method == 'GET':
#         menu_items = [{'id': item.id, 'name': item.name, 'price': item.price} for item in menu.items]
#         return jsonify(menu_items)
#
#     if claims['role'] != 'admin' and menu.restaurant_id != int(user_restaurant_id):
#         return jsonify({'message': 'Access denied'}), 403
#
#
#     elif request.method == 'POST':
#         name = request.form.get('name')
#         price = request.form.get('price')
#         if not name or not price:
#             return jsonify({'message': 'Name and price are required'}), 400
#         new_menu_item = MenuItem(name=name, price=float(price), menu_id=menu_id)
#         db.session.add(new_menu_item)
#         db.session.commit()
#         return jsonify({'message': 'Menu item added successfully'}), 201
#
#     elif request.method == 'PUT' or request.method == 'DELETE':
#         item_name = request.form.get('name')
#         menu_item = MenuItem.query.filter_by(menu_id=menu_id, name=item_name).first()
#         if not menu_item:
#             return jsonify({'message': 'No such item in your menu'}), 404
#
#         if request.method == 'PUT':
#             new_price = request.form.get('price')
#             if not new_price:
#                 return jsonify({'message': 'Price is required'}), 400
#             menu_item.price = float(new_price)
#             db.session.commit()
#             return jsonify({'message': 'Menu item updated successfully'})
#
#         elif request.method == 'DELETE':
#             db.session.delete(menu_item)
#             db.session.commit()
#             return jsonify({'message': 'Menu item deleted successfully'})
#
#     return jsonify({'message': 'Invalid request'}), 400
#
#
# @restaurant_bp.route('/order/accept/order_id', methods=['POST'])
# def accept_order():
#
#     # Tworzenie danych zamówienia w formacie JSON
#     order_data = {
#         "order_id": random.randint(1,10000),
#         "restaurant_id": 456,
#         "username": "krzychu123",
#         "items": [
#             {"product_id": 1, "quantity": 2},
#             {"product_id": 2, "quantity": 1}
#         ],
#         "total_price": 99.99,
#         "status": 'being_prepared'
#
#     }
#
#     with connection.Producer() as producer:
#         producer.publish(
#             json.dumps(order_data),
#             exchange=orders_exchange,
#             routing_key='orders',
#             declare=[orders_queue]
#         )
#     # Zwracanie odpowiedzi
#     return jsonify({'status': 'accepted', 'order': order_data}), 202
#
#
# @restaurant_bp.route('/order/reject', methods=['POST'])
# def reject_order():
#     order_data = request.get_json()
#     return jsonify({'status': 'rejected', 'order': order_data}), 200
