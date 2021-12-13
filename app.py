import os
import re

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import User, UserRegister, UserLogin, TokenRefresh, UserLogout
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from blocklist import BLOCKLIST


app = Flask(__name__)
env_db_var = os.environ.get('DATABASE_URI', 'sqlite:///data.db')     # Same Folder
if env_db_var.startswith("postgres://"):
    uri = env_db_var.replace("postgres://", "postgresql://", 1) # Fix MySQLAlchemy version bugs
app.config['SQLALCHEMY_DATABASE_URI'] = env_db_var
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # Turns off Flask tracker, to use only SQLAlchemy tracker
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'password'
#app.config['JWT_SECRET_KEY'] = True
api = Api(app)



jwt = JWTManager(app)  # send user and password with authenticate, if match uses de JWT token in identity to search the user that is token represents

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload['jti'] in BLOCKLIST

@jwt.additional_claims_loader
def add_claims_to_jwt(sub):     # sub has the user.id value
    if sub == 1:                # First user will be admin
        return {'is_admin': True}
    return {'is_admin': False}

@jwt.expired_token_loader
def expired_token_callbak(jwt_header, jwt_payload):
    return jsonify({'description':'The token has expired.',
                    'error': 'token expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callbak(error):
    return jsonify({'description':'Signature verification failed.',
                    'error': 'invalid_token'}),401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "description": "The token has been revoked.",
        'error': 'token_revoked'
    }), 401


api.add_resource(Store, '/store/<string:name>')
api.add_resource(Item, '/item/<string:name>') # https://127.0.0.1:5000/item/Exemplo
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')


if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)  # debug=True para desenvolver
