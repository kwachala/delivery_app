from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from . import db
from .models import Restaurant, Menu, MenuItem
from .utils import admin_required

restaurant_bp = Blueprint('restaurant', __name__)


@restaurant_bp.route('/restaurants', methods=['GET', 'POST'])
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


# if __name__ == '__main__':
#     with restaurant_app.app_context():
#         db.create_all()
#
#     restaurant_app.run(debug=True)
