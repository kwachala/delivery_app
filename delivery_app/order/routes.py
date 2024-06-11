from flask import request, jsonify, Blueprint
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity,
)

from . import db
from .models import Order, OrderItem
from .utils import admin_required, serialize_order_item
import json

order_bp = Blueprint("order", __name__)


@order_bp.route("/orders", methods=["GET", "POST", "DELETE"])
@jwt_required()
def handle_orders():
    claims = get_jwt()
    if request.method == "POST":
        if not claims or claims["role"] != "CUSTOMER":
            return jsonify({"message": "Only user can create orders"}), 403

        restaurant_id = request.form.get("restaurant_id")
        username = get_jwt_identity()

        # TO DO
        # Zapytanie, czy istnieje restauracja

        if not restaurant_id:
            return jsonify({"message": "Restaurant id required to create order"}), 400

        new_order = Order(
            restaurant_id=restaurant_id, username=username, total_price=0.0
        )
        db.session.add(new_order)
        db.session.commit()

        return jsonify({"message": "Order created successfully"}), 201

    if not claims or claims["role"] != "ADMIN":
        return jsonify({"message": "Administrative privileges required"}), 403
    orders = Order.query.all()
    return jsonify(
        [
            {
                "id": o.id,
                "restaurant_id": o.restaurant_id,
                "username": o.username,
                "items": [serialize_order_item(item) for item in o.items],
                "total_price": o.total_price,
            }
            for o in orders
        ]
    )


@order_bp.route("/order/<int:order_id>", methods=["GET", "DELETE"])
@jwt_required()
def handle_order(order_id):
    order = Order.query.get_or_404(order_id)
    claims = get_jwt()
    username = get_jwt_identity()

    if request.method == "GET":
        if claims["role"] == "CUSTOMER":
            if username != order.username:
                return (
                    jsonify({"message": "This order does not belong to this user"}),
                    401,
                )
            else:
                return jsonify(
                    {
                        "id": order.id,
                        "restaurant_id": order.restaurant_id,
                        "username": order.username,
                        "items": [serialize_order_item(item) for item in order.items],
                        "total_price": order.total_price,
                    }
                )
        elif claims["role"] == "ADMIN":
            return jsonify(
                {
                    "id": order.id,
                    "restaurant_id": order.restaurant_id,
                    "username": order.username,
                    "items": [serialize_order_item(item) for item in order.items],
                    "total_price": order.total_price,
                }
            )
        else:
            return jsonify({"message": "Not authorized"}), 401

    elif request.method == "DELETE":
        if claims["role"] == "ADMIN" or (
            claims["role"] == "CUSTOMER" and order.username == username
        ):
            db.session.delete(order)
            db.session.commit()
            return jsonify({"message": "Order deleted successfully"})
        else:
            return jsonify({"message": "Not authorized"}), 401


@order_bp.route("/add_item/<int:order_id>", methods=["POST"])
@jwt_required()
def add_item(order_id):
    order = Order.query.get_or_404(order_id)

    item_name = request.form.get("name")

    try:
        item_price = float(request.form.get("price"))
    except ValueError:
        return (
            jsonify({"message": "Price of an order item has to be a number"}),
            400,
        )

    new_order_item = OrderItem(order_id=order.id, name=item_name, price=item_price)

    order.items.append(new_order_item)
    order.total_price += new_order_item.price

    db.session.add(new_order_item)
    db.session.commit()

    return (
        jsonify({"message": "Added item to the order"}),
        201,
    )


@order_bp.route("/order_item/<int:order_item_id>", methods=["DELETE", "PUT"])
def handle_order_item(order_item_id):
    order_item = OrderItem.query.get(order_item_id)
    order = Order.query.get_or_404(order_item.order_id)

    if request.method == "DELETE":
        order.total_price -= order_item.price
        db.session.delete(order_item)
        db.session.commit()
        return jsonify({"message": "Order item deleted successfully"}), 200
    else:
        new_name = request.form.get("name", None)
        new_price = request.form.get("price", None)

        if new_name:
            order_item.name = new_name
        if new_price:
            try:
                new_price = float(new_price)
            except ValueError:
                return (
                    jsonify({"message": "Price of an order item has to be a number"}),
                    400,
                )

            order.total_price -= order_item.price
            order.total_price += new_price
            order_item.price = new_price

        db.session.commit()

        return (
            jsonify(
                [
                    {"message": "Order item details updated successfully"},
                    {
                        "id": order_item.id,
                        "name": order_item.name,
                        "price": order_item.price,
                    },
                ]
            ),
            200,
        )


@order_bp.route("/send_order_for_accept/<int:order_id>", methods=["GET"])
def send_order_for_accept(order_id):
    from .tasks import send_order_to_queue

    order = Order.query.get_or_404(order_id)

    if len(order.items) == 0:
        return jsonify({"message": "This order is empty"}), 400

    order_data = {
        "id": order.id,
        "restaurant_id": order.restaurant_id,
        "username": order.username,
        "total_price": order.total_price,
        "items": [serialize_order_item(item) for item in order.items],
    }

    send_order_to_queue.delay(json.dumps(order_data))

    return jsonify({"status": "send_for_accept", "order": order_data}), 202
