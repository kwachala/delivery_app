from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
import threading
from . import db
from .models import Restaurant, Menu, MenuItem

deliveries_bp = Blueprint('deliveries', __name__)

