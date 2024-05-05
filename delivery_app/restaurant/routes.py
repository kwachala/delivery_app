from functools import wraps

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.config['JWT_SECRET_KEY'] = 'super-secret'

db = SQLAlchemy(app)
jwt = JWTManager(app)


# Definicje modeli bazy danych
class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(120), nullable=False)


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    items = db.relationship('MenuItem', backref='menu', lazy=True)


class MenuItem(db.Model):
    __tablename__ = 'menuitem'  # Jawne określenie nazwy tabeli
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims['role'] != 'admin':
            return jsonify(msg='Administration privileges required'), 403
        return fn(*args, **kwargs)

    return wrapper


def restauration_or_admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims['role'] != 'admin' and claims['role'] != 'restaurant':
            return jsonify(msg='Administration or restaurant privileges required'), 403
        return fn(*args, **kwargs)

    return wrapper


@app.route('/login', methods=['POST'])
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


@app.route('/restaurants', methods=['GET', 'POST'])
@jwt_required()
def handle_restaurants():
    if request.method == 'POST':
        # Tylko admin może tworzyć nowe restauracje
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

    # Metoda GET jest dostępna dla wszystkich uwierzytelnionych użytkowników
    restaurants = Restaurant.query.all()
    return jsonify([{'id': r.id, 'name': r.name, 'address': r.address} for r in restaurants])


@app.route('/restaurants/<int:restaurant_id>', methods=['GET', 'PUT', 'DELETE'])
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


@app.route('/menu/<int:menu_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def handle_menu(menu_id):
    claims = get_jwt()
    menu = Menu.query.get_or_404(menu_id)
    user_restaurant_id = claims['restaurant_id']

    if request.method == 'GET':
        # Zwrócenie wszystkich elementów menu
        menu_items = [{'id': item.id, 'name': item.name, 'price': item.price} for item in menu.items]
        return jsonify(menu_items)

    if claims['role'] != 'admin' and menu.restaurant_id != int(user_restaurant_id):
        return jsonify({'message': 'Access denied'}), 403


    elif request.method == 'POST':
        # Dodanie nowego elementu do menu
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
        # Szukanie produktu w menu
        menu_item = MenuItem.query.filter_by(menu_id=menu_id, name=item_name).first()
        if not menu_item:
            return jsonify({'message': 'No such item in your menu'}), 404

        if request.method == 'PUT':
            # Aktualizacja istniejącego elementu menu
            new_price = request.form.get('price')
            if not new_price:
                return jsonify({'message': 'Price is required'}), 400
            menu_item.price = float(new_price)
            db.session.commit()
            return jsonify({'message': 'Menu item updated successfully'})

        elif request.method == 'DELETE':
            # Usunięcie elementu z menu
            db.session.delete(menu_item)
            db.session.commit()
            return jsonify({'message': 'Menu item deleted successfully'})

    return jsonify({'message': 'Invalid request'}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
