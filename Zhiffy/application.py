from flask import Flask
import bcrypt
from flask_pymongo import PyMongo

from bson.json_util import dumps

from bson.objectid import ObjectId

from flask import jsonify, request

from werkzeug.security import generate_password_hash, check_password_hash

from pymongo import MongoClient

from flask_jwt_extended import JWTManager, jwt_required, create_access_token


dbClient = MongoClient("mongodb://localhost:27017/")

db = dbClient["application_db"]

zhiffy = db["Zhiffy"]
items = db["Items"]

app = Flask(__name__)
jwt = JWTManager(app)

app.config["JWT_SECRET_KEY"] = "ACCESS_KEY_999"
#mongo = PyMongo(app)


@app.route("/register", methods=["POST"])
def register():
    user_email = request.form["email"]

    is_inValid = zhiffy.find_one({"email": user_email})

    if is_inValid:
        return jsonify(message="Cannot Register User. Email Already Used"), 409
    else:
        user_name = request.form["name"]
        user_password = request.form["password"]
        password_new = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())
        user_data = dict(name=user_name, email=user_email, password=password_new)
        zhiffy.insert_one(user_data)
        user_access_token = create_access_token(identity=user_email)

        return jsonify(message="Voila! User Registration Successful.", access_token=user_access_token), 201


@app.route("/login", methods=["POST"])
def login():

    _json = request.json
    user_email = _json["email"]
    user_password = _json["password"]

    current_user = zhiffy.find_one({'email': user_email})

    if current_user:
        if bcrypt.hashpw(user_password.encode('utf-8'), current_user["password"]) == current_user["password"]:
            user_access_token = create_access_token(identity=user_email)
            return jsonify(message="Voila! User Successfully Logged In.", access_token=user_access_token)

    return "Invalid Credentials. Please Retry."

@app.route("/changeUserDetails/<uid>", methods=["PUT"])
@jwt_required()
def changeUserDetail(uid):
    _json = request.json
    user_email = _json["email"]
    user_name = _json["name"]
    user_password = _json["password"]
    hash_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())

    update_user = zhiffy.update_one({'_id': ObjectId(uid)}, {"$set": {'email': user_email, 'name': user_name, 'password': hash_password}})

    return jsonify(message="User Details with Email {"+user_email+"} and ID {"+str(ObjectId(uid))+"} Updated.")


@app.route("/insertProducts", methods=["POST"])
@jwt_required()
def insertProducts():
    _json = request.json
    item_category = _json["category"]
    item_brand = _json["brand"]
    item_model = _json["model"]
    item_purchase = _json["purchase_date"]
    item_price = _json["price"]
    item_location = _json["location"]

    if item_category and item_brand and item_purchase and item_purchase and item_price and item_location and request.method == 'POST':
        item_data = dict(category=item_category, brand=item_brand, model=item_model, purchase_date=item_purchase, price=item_price, location=item_location)
        
        id = items.insert_one(item_data)
        return jsonify(message="Item Added Successfully")
    
    return jsonify(message="Please complete all the fields")



@app.route("/seeAllProducts", methods=["GET"])
def getAllItems():
    allItems = items.find()
    results = dumps(allItems)
    return results



@app.route("/seeAllProducts/<pid>", methods=["GET"])
def getItemDetails(pid):
    item = items.find_one({"_id": ObjectId(pid)})
    result = dumps(item)
    return result



@app.route("/deleteProduct/<pid>", methods=["DELETE"])
def deleteGivenItem(pid):
    
    result = jsonify("Item with ID {"+str(ObjectId(pid))+"} Deleted Successfully.")
    items.delete_one({"_id": ObjectId(pid)})
    result.status_code = 200

    return result

    
@app.route("/changeItemDetails/<pid>", methods=["PUT"])
def changeItemDetail(pid):
    _json = request.json

    item_category = _json["category"]
    item_brand = _json["brand"]
    item_model = _json["model"]
    item_purchase = _json["purchase_date"]
    item_price = _json["price"]
    item_location = _json["location"]

    update_item = items.update_one({'_id': ObjectId(pid)}, {"$set": {'category': item_category, 'brand': item_brand, 'model': item_model, 'purchase_date': item_purchase, 'price': item_price, 'location': item_location}})
    
    return jsonify(message="Item Details with ID {"+str(ObjectId(pid))+"} Updated.")

    

if __name__ == '__main__':
    app.run(host="localhost", debug=True)


        




