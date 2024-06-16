import requests
from flask import request, jsonify, Blueprint, current_app
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity,
)

from . import db
from .models import Order, OrderItem
from .utils import admin_required, serialize_order_item
from .tasks import send_order_to_queue
import json

order_bp = Blueprint("order", __name__)


@order_bp.route("/orders", methods=["GET", "POST"])
@jwt_required()
def handle_orders():
    claims = get_jwt()
    if request.method == "POST":
        if not claims or claims["role"] != "CUSTOMER":
            return jsonify({"message": "Only customer can create orders"}), 403

        restaurant_id = request.json.get("restaurant_id")
        username = claims["sub"]

        if not restaurant_id:
            return jsonify({"message": "Restaurant id required to create order"}), 400

        items = request.json.get("items")

        if not items:
            return jsonify({"message": "Order items are required"}), 400

        # Create the new order
        new_order = Order(
            restaurant_id=restaurant_id, username=username, total_price=0.0, status="placed"
        )
        db.session.add(new_order)
        db.session.flush()  # Flush to get new_order.id

        item_ids = [item.get("menu_item_id") for item in items]
        quantities = {item.get("menu_item_id"): item.get("quantity") for item in items}

        # Fetch menu item details from restaurant microservice in a single request
        response = requests.get("http://restaurant-app:5000/restaurant_api/menu_items", json={"item_ids": item_ids})
        if response.status_code != 200:
            return jsonify({"message": "Error fetching menu items from restaurant service"}), response.status_code

        menu_items = response.json()

        total_price = 0.0
        order_items = []

        # Prepare order items and calculate total price
        for menu_item in menu_items:
            menu_item_id = menu_item["id"]
            name = menu_item["name"]
            price = menu_item["price"]
            quantity = quantities[menu_item_id]

            total_price += price * quantity

            order_item = OrderItem(
                order_id=new_order.id,
                name=name,
                price=price,
                quantity=quantity
            )
            order_items.append(order_item)

        # Add order items to session
        for order_item in order_items:
            db.session.add(order_item)

        # Update the order with the total price
        new_order.total_price = total_price
        db.session.commit()

        return jsonify({"message": "Order created successfully", "order_id": new_order.id}), 201

    if not claims or claims["role"] != "ADMIN":
        return jsonify({"message": "Administrative privileges required"}), 403

    orders = Order.query.all()
    return jsonify(
        [
            {
                "id": o.id,
                "restaurant_id": o.restaurant_id,
                "username": o.username,
                "total_price": o.total_price,
                "status": o.status,
                "items": [serialize_order_item(item) for item in o.items]
            }
            for o in orders
        ]
    )


@order_bp.route("/order/<int:order_id>", methods=["GET"])
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
                        "total_price": order.total_price,
                        "status": order.status,
                        "items": [serialize_order_item(item) for item in order.items]
                    }
                )
        elif claims["role"] == "ADMIN":
            return jsonify(
                {
                    "id": order.id,
                    "restaurant_id": order.restaurant_id,
                    "username": order.username,
                    "total_price": order.total_price,
                    "status": order.status,
                    "items": [serialize_order_item(item) for item in order.items]
                }
            )
        else:
            return jsonify({"message": "Not authorized"}), 401


@order_bp.route("/send_order_for_accept/<int:order_id>", methods=["GET"])
def send_order_for_accept(order_id):
    order = Order.query.get_or_404(order_id)

    if len(order.items) == 0:
        return jsonify({"message": "This order is empty"}), 400

    order_data = {
        "id": order.id,
        "restaurant_id": order.restaurant_id,
        "username": order.username,
        "total_price": order.total_price,
        "status": order.status,
        "items": [serialize_order_item(item) for item in order.items]
    }

    # Przygotowanie danych do płatności
    payu_order_data = prepare_payu_order_data(order)

    # Tworzenie zamówienia w PayU
    response_data = create_payu_order(payu_order_data)

    if 'redirectUri' not in response_data:
        return jsonify({"message": "Failed to create PayU order"}), 500

    # Zwracanie URL do przekierowania użytkownika na stronę płatności PayU
    return jsonify({"redirectUri": response_data["redirectUri"]}), 202

    # send_order_to_queue.delay(json.dumps(order_data))

    # return jsonify({"status": "send_for_accept", "order": order_data}), 202


# Przygotowanie danych w taki sposób, aby mogły zostać wysłane do payu sandbox
def prepare_payu_order_data(order):
    return {
        "notifyUrl": "http://localhost:5003/notify",
        "customerIp": "127.0.0.1",
        "merchantPosId": current_app.config['PAYU_POS_ID'],
        "description": f"Order {order.id}",
        "currencyCode": "PLN",
        "totalAmount": int(order.total_price * 100),  # w groszach
        "buyer": {
            "username": order.username
        },
        "products": [
            {
                "name": item.name,
                "unitPrice": int(item.price * 100),  # w groszach
                "quantity": 1
            } for item in order.items
        ]
    }


# przygotowanie zapytania do payu
def create_payu_order(payu_order_data):
    token = get_payu_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = "https://secure.snd.payu.com/api/v2_1/orders"
    response = requests.post(url, headers=headers, json=payu_order_data)
    response.raise_for_status()

    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Invalid JSON response"}

    return response_data


# pobranie access tokena dla payu
def get_payu_access_token():
    url = "https://secure.snd.payu.com/pl/standard/user/oauth/authorize"
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": current_app.config['PAYU_CLIENT_ID'],
        "client_secret": current_app.config['PAYU_CLIENT_SECRET']
    }
    response = requests.post(url, data=auth_data)
    response_data = response.json()
    return response_data["access_token"]


@order_bp.route('/notify', methods=['POST'])
def notify():
    notification = request.json
    order_id = notification['order']['order_id']
    order_status = notification['order']['status']

    if order_status == 'COMPLETED':
        order = Order.query.get(order_id)

        order_data = {
            "id": order.id,
            "restaurant_id": order.restaurant_id,
            "username": order.username,
            "total_price": order.total_price,
            "status": order.status,
            "items": [serialize_order_item(item) for item in order.items],
        }

        order.status = "paid"
        db.session.commit()

        # Przekazanie zamówienia do kolejki RabbitMQ
        send_order_to_queue.delay(json.dumps(order_data))

        return jsonify({"status": "success", "order_data": order_data}), 200

    return jsonify({"status": "ignored"}), 200



# @order_bp.route("/add_item/<int:order_id>", methods=["POST"])
# @jwt_required()
# def add_item(order_id):
#     order = Order.query.get_or_404(order_id)
#
#     item_name = request.form.get("name")
#
#     try:
#         item_price = float(request.form.get("price"))
#     except ValueError:
#         return (
#             jsonify({"message": "Price of an order item has to be a number"}),
#             400,
#         )
#
#     new_order_item = OrderItem(order_id=order.id, name=item_name, price=item_price)
#
#     order.items.append(new_order_item)
#     order.total_price += new_order_item.price
#
#     db.session.add(new_order_item)
#     db.session.commit()
#
#     return (
#         jsonify({"message": "Added item to the order"}),
#         201,
#     )
#
#
# @order_bp.route("/order_item/<int:order_item_id>", methods=["DELETE", "PUT"])
# def handle_order_item(order_item_id):
#     order_item = OrderItem.query.get(order_item_id)
#     order = Order.query.get_or_404(order_item.order_id)
#
#     if request.method == "DELETE":
#         order.total_price -= order_item.price
#         db.session.delete(order_item)
#         db.session.commit()
#         return jsonify({"message": "Order item deleted successfully"}), 200
#     else:
#         new_name = request.form.get("name", None)
#         new_price = request.form.get("price", None)
#
#         if new_name:
#             order_item.name = new_name
#         if new_price:
#             try:
#                 new_price = float(new_price)
#             except ValueError:
#                 return (
#                     jsonify({"message": "Price of an order item has to be a number"}),
#                     400,
#                 )
#
#             order.total_price -= order_item.price
#             order.total_price += new_price
#             order_item.price = new_price
#
#         db.session.commit()
#
#         return (
#             jsonify(
#                 [
#                     {"message": "Order item details updated successfully"},
#                     {
#                         "id": order_item.id,
#                         "name": order_item.name,
#                         "price": order_item.price,
#                     },
#                 ]
#             ),
#             200,
#         )
