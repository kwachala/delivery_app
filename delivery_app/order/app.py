from . import order_app
from . import db
from .models import Order, OrderItem

if __name__ == "__main__":
    order_app.run(debug=True)
