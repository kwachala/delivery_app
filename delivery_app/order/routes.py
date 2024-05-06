from flask import request, jsonify, Blueprint
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity,
)

from . import db
from delivery_app.order.models import Order, OrderItem
from delivery_app.restaurant.utils import admin_required

order_bp = Blueprint("order", __name__)


@order_bp.route("/orders", methods=["GET", "POST", "DELETE"])
@jwt_required()
def handle_orders():
    claims = get_jwt()
    if request.method == "POST":
        if "role" not in claims or claims["role"] != "user":
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

    if "role" not in claims or claims["role"] != "admin":
        return jsonify({"message": "Administrative privileges required"}), 403
    orders = Order.query.all()
    return jsonify(
        [
            {"id": o.id, "restaurant_id": o.restaurant_id, "username": o.username}
            for o in orders
        ]
    )


@order_bp.route("/order/<int:order_id>", methods=["GET", "DELETE"])
@jwt_required()
@admin_required
def handle_order(order_id):
    order = Order.query.get_or_404(order_id)

    if request.method == "GET":
        return jsonify(
            {
                "id": order.id,
                "restaurant_id": order.restaurant_id,
                "username": order.username,
                "total_price": order.total_price,
            }
        )

    elif request.method == "DELETE":
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "Order deleted successfully"})
