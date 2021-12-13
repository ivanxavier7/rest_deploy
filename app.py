import os
import re

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import User, UserRegister, UserLogin
from resources.item import Item, ItemList
from resources.store import Store, StoreList


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


@jwt.additional_claims_loader
def add_claims_to_jwt(sub):     # sub has the user.id value
    if sub == 1:                # First user will be admin
        return {'is_admin': True}
    return {'is_admin': False}


api.add_resource(Store, '/store/<string:name>')
api.add_resource(Item, '/item/<string:name>') # https://127.0.0.1:5000/item/Exemplo
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')


if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)  # debug=True para desenvolver
