from . import user_app
from . import db2
from .models import Restaurant, Menu, MenuItem

if __name__ == '__main__':
    user_app.run(debug=True)
