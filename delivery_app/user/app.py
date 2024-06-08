from . import user_app
from . import user_db
from .models import User

if __name__ == '__main__':
    user_app.run(debug=True)
