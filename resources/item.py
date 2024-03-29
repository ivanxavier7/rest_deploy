from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity
    )
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'price',
        type=float,
        required=True,
        help="This field cannot be left blank!"
        )
    parser.add_argument(
        'store_id',
        type=int,
        required=True,
        help="Every item needs a store id."
        )
    
    @jwt_required()   # Decorator that require de authentication before "get"
    def get(self, name):
        item =ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404
    
    @jwt_required(fresh=False) # Need fresh token to be false
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400  # BAD REQUEST
        
        data = Item.parser.parse_args()
        item = ItemModel(name, **data)
        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred while inserting the item."}, 500 # INTERNAL SERVER ERROR
        return item.json(), 201                # CREATED
    

    @jwt_required()
    def delete(self, name):
        claims = get_jwt()   # Claim data from token, is this case just admin can delete items
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401
        
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        return {'message': 'Item deleted.'}

    def put(self, name):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)
        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']
            item.store_id = data['store_id']
            
        item.save_to_db()
        
        return item.json()
    

class ItemList(Resource):
    @jwt_required(optional=True)
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]    # With user_id get's all info
        if user_id:
            return {'items': 200}
        return {'items': [item['name'] for item in items],
                'message': 'More data available if you log in.'}, 200  # Without user_id just get the name, without login