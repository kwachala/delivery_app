import logging

from flask import request, jsonify, Blueprint
import json
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
import threading
from . import db
from .models import Delivery, DeliveryItem
from .utils import to_dict

deliveries_bp = Blueprint('deliveries', __name__)


@deliveries_bp.route('/deliveries', methods=['GET'])
def check_current_deliveries():
    deliveries = Delivery.query.all()

    return jsonify([{'id': d.id, 'restaurant_id': d.restaurant_id, 'username': d.username, 'items': d.items,
                     'total_price': d.total_price, 'deliverer_id': d.deliverer_id} for d in deliveries])


@deliveries_bp.route('/deliveries/available', methods=['GET'])
def get_available_deliveries():
    deliveries = Delivery.query.filter_by(status='available').all()
    return jsonify([delivery.to_dict() for delivery in deliveries])


@deliveries_bp.route('/deliveries/<int:delivery_id>/accept', methods=['POST'])
@jwt_required()
def accept_delivery(delivery_id):
    claims = get_jwt()
    if not claims or claims['user_id'] != "DELIVERER":
        return jsonify({"message": "Only deliverer can accept deliveries"}), 403

    delivery = Delivery.query.get(delivery_id)
    if delivery and delivery.status == 'available':
        delivery.status = 'in_progress'
        delivery.deliverer_id = claims['user_id']
        db.session.commit()
        return jsonify(delivery.to_dict()), 200
    return jsonify({'error': 'Delivery not found or not available'}), 404


@deliveries_bp.route('/deliveries/<int:delivery_id>', methods=['GET'])
def get_delivery_details(delivery_id):
    delivery = Delivery.query.get(delivery_id)
    if delivery:
        return jsonify(delivery.to_dict())
    return jsonify({'error': 'Delivery not found'}), 404


@deliveries_bp.route('/deliveries/<int:delivery_id>/complete', methods=['POST'])
def complete_delivery(delivery_id):
    delivery = Delivery.query.get(delivery_id)
    if delivery and delivery.status == 'in_progress':
        delivery.status = 'completed'
        db.session.commit()
        return jsonify(delivery.to_dict()), 200
    return jsonify({'error': 'Delivery not found or not in progress'}), 404


@deliveries_bp.route('/add_delivery', methods=['POST'])
def add_delivery():
    data = request.json
    new_delivery = Delivery(
        restaurant_id=data['restaurant_id'],
        username=data['username'],
        items=data['items'],
        total_price=data['total_price'],
        status=data.get['status'],
        deliverer_id=data.get['deliverer_id']
    )
    db.session.add(new_delivery)
    db.session.commit()

    return jsonify({'delivery_added': True, 'delivery': new_delivery})


# @deliveries_bp.route('/get_delivery', methods=['POST'])
# def get_delivery():
#     order_data = (request.get_json())
#     username = order_data.get('username')
#     restaurant_id = order_data.get('restaurant_id')
#     items = order_data.get('items')