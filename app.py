import os

from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from resources.user import UserRegister
from resources.item import Item, ItemList
from resources.store import Store, StoreList

from security import authenticate, identity


app = Flask(__name__)
env_db_var = os.environ.get('DATABASE_URL', 'sqlite:///data.db')     # Same Folder
if env_db_var.startswith("postgres://"):
    uri = env_db_var.replace("postgres://", "postgresql://", 1) # Fix MySQLAlchemy version bugs
app.config['SQLALCHEMY_DATABASE_URI'] = env_db_var
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # Turns off Flask tracker, to use only SQLAlchemy tracker
app.secret_key = 'password'
api = Api(app)



jwt = JWT(app, authenticate, identity)  # Create new endpoit /auth, send user and password with authenticate, if match uses de JWT token in identity to search the user that is token represents

api.add_resource(Store, '/store/<string:name>')
api.add_resource(Item, '/item/<string:name>') # https://127.0.0.1:5000/item/Exemplo
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')



if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)  # debug=True para desenvolver
