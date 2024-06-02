import logging

from flask import request, jsonify, Blueprint
import json
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
import threading
from . import db
from .models import Restaurant, Menu, MenuItem, Delivery

deliveries_bp = Blueprint('deliveries', __name__)


@deliveries_bp.route('/deliveries', methods=['GET'])
def check_current_deliveries():
    delivery = Delivery.query.all()

    return jsonify([{'id': d.id, 'restaurant_id': d.restaurant_id, 'username': d.username, 'items': d.items,
                     'total_price': d.total_price, 'deliverer_id': d.deliverer_id} for d in delivery])


@deliveries_bp.route('/add_delivery', methods=['POST'])
def add_delivery():
    order_data = (request.get_json())
    username = order_data.get('username')
    restaurant_id = order_data.get('restaurant_id')
    items = order_data.get('items')
    items = json.dumps(items)
    total_price = order_data.get('total_price')
    status = order_data.get('status')

    new_delivery = Delivery(
        restaurant_id=restaurant_id,
        username=username,
        items=items,
        total_price=total_price,
        status=status,
        deliverer_id='ZBYCHU'
    )

    db.session.add(new_delivery)
    db.session.commit()

    return jsonify({'delivery_added': True})

@deliveries_bp.route('/get_delivery', methods=['POST'])
def get_delivery():
    order_data = (request.get_json())
    username = order_data.get('username')
    restaurant_id = order_data.get('restaurant_id')
    items = order_data.get('items')