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

# temporary
@restaurant_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', None)
    password = request.form.get('password', None)
    role = request.form.get('role', None)
    try:
        restaurant_id = request.form.get('restaurant_id', None)
    except:
        restaurant_id = None

    access_token = create_access_token(identity=username,
                                       additional_claims={'role': role, 'restaurant_id': restaurant_id})
    return jsonify(access_token=access_token)


@restaurant_bp.route('/restaurants', methods=['GET', 'POST'])
@jwt_required()
def handle_restaurants():
    if request.method == 'POST':
        claims = get_jwt()

        if 'role' not in claims or claims['role'] != 'ADMIN':
            return jsonify({'message': 'Administrative privileges required'}), 403

        name = request.form.get('name')
        address = request.form.get('address')
        if not name or not address:
            return jsonify({'message': 'Name and address are required'}), 400

        new_restaurant = Restaurant(name=name, address=address)
        db.session.add(new_restaurant)
        db.session.flush()

        new_menu = Menu(restaurant_id=new_restaurant.id)
        db.session.add(new_menu)
        db.session.commit()

        return jsonify({'message': 'Restaurant created successfully'}), 201

    restaurants = Restaurant.query.all()

    return jsonify([{'id': r.id, 'name': r.name, 'address': r.address} for r in restaurants])


@restaurant_bp.route('/restaurants/<int:restaurant_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@admin_required
def handle_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    if request.method == 'GET':
        return jsonify({'id': restaurant.id, 'name': restaurant.name, 'address': restaurant.address})

    elif request.method == 'PUT':
        name = request.form.get('name')
        address = request.form.get('address')
        if not name or not address:
            return jsonify({'message': 'Name and address are required'}), 400

        restaurant.name = name
        restaurant.address = address
        db.session.commit()
        return jsonify({'message': 'Restaurant updated successfully'})

    elif request.method == 'DELETE':
        db.session.delete(restaurant)
        db.session.commit()
        return jsonify({'message': 'Restaurant deleted successfully'})


@restaurant_bp.route('/menu/<int:menu_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def handle_menu(menu_id):
    claims = get_jwt()
    menu = Menu.query.get_or_404(menu_id)
    user_restaurant_id = claims['restaurant_id']

    if request.method == 'GET':
        menu_items = [{'id': item.id, 'name': item.name, 'price': item.price} for item in menu.items]
        return jsonify(menu_items)

    if claims['role'] != 'admin' and menu.restaurant_id != int(user_restaurant_id):
        return jsonify({'message': 'Access denied'}), 403


    elif request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        if not name or not price:
            return jsonify({'message': 'Name and price are required'}), 400
        new_menu_item = MenuItem(name=name, price=float(price), menu_id=menu_id)
        db.session.add(new_menu_item)
        db.session.commit()
        return jsonify({'message': 'Menu item added successfully'}), 201

    elif request.method == 'PUT' or request.method == 'DELETE':
        item_name = request.form.get('name')
        menu_item = MenuItem.query.filter_by(menu_id=menu_id, name=item_name).first()
        if not menu_item:
            return jsonify({'message': 'No such item in your menu'}), 404

        if request.method == 'PUT':
            new_price = request.form.get('price')
            if not new_price:
                return jsonify({'message': 'Price is required'}), 400
            menu_item.price = float(new_price)
            db.session.commit()
            return jsonify({'message': 'Menu item updated successfully'})

        elif request.method == 'DELETE':
            db.session.delete(menu_item)
            db.session.commit()
            return jsonify({'message': 'Menu item deleted successfully'})

    return jsonify({'message': 'Invalid request'}), 400


@restaurant_bp.route('/order/accept/order_id', methods=['POST'])
def accept_order():

    # Tworzenie danych zamówienia w formacie JSON
    order_data = {
        "order_id": random.randint(1,10000),
        "restaurant_id": 456,
        "username": "krzychu123",
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1}
        ],
        "total_price": 99.99,
        "status": 'being_prepared'

    }

    with connection.Producer() as producer:
        producer.publish(
            json.dumps(order_data),
            exchange=orders_exchange,
            routing_key='orders',
            declare=[orders_queue]
        )
    # Zwracanie odpowiedzi
    return jsonify({'status': 'accepted', 'order': order_data}), 202


@restaurant_bp.route('/order/reject', methods=['POST'])
def reject_order():
    order_data = request.get_json()
    return jsonify({'status': 'rejected', 'order': order_data}), 200
