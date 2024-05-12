from . import restaurant_app
from . import db
from .models import Restaurant, Menu, MenuItem

if __name__ == '__main__':
    restaurant_app.run(debug=True)
