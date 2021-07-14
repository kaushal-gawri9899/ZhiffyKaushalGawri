"""
Importing the necessary Libraries
"""
from flask import Flask
import bcrypt
from flask_pymongo import PyMongo

from bson.json_util import dumps

from bson.objectid import ObjectId

from flask import jsonify, request

from pymongo import MongoClient

from flask_jwt_extended import JWTManager, jwt_required, create_access_token

#Use MongoClient to connect to the local MongoDB instance
dbClient = MongoClient("mongodb://localhost:27017/")

#Create a database for the application
db = dbClient["application_db"]

#database created will have multiple collections, 
# one for storing all the registered user details 
# other for storing all the product details
zhiffy = db["Zhiffy"]
items = db["Items"]

#Creating a flask app and configuring that with JWTManager to secure the entire app
app = Flask(__name__)
jwt = JWTManager(app)

app.config["JWT_SECRET_KEY"] = "ACCESS_KEY_999"


"""
Register API route : Used for registering users to the system and adding to Zhiffy collection
Uses bcrypt python library to hash the passwords that user enters using random salts after the password is encoded
Returns an access token with a successfull registeration message
Error handling for empty strings could be added using a simple if conditions but skipped for now
As suggested in specification, details from form data acts as input.
"""
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


"""
Login API route : Used for providing access to users for the system
Uses bcrypt python library to hash the passwords that user enters using random salts after the password is encoded
Hashed password is compared to the password stored in collection and authorization is completed
Returns an access token with a successfull login message
Access Token is used for authorizatioton in other methods
Error handling for empty strings could be added using a simple if conditions but skipped for now
As suggested in specification, login details are taken as json string
"""
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

"""
Change User Detail API route : Used to update the details of user stored in collection
Uses PUT Http request to replace the current details with the newly updated one
Returns a success message
A decorator is added to add security for the current method, user with only access token provided during login can perform operation
"""
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


"""
Insert Product API route : Adds a product or items to the collection with pre decided attributes. 
Pre decided attributes are used to the best of my knowledge
Validates empty string for details and converts the values to a dictionary
Dictionary is then added to the "items" collection
Returns a success message
A decorator is added to add security for the current method, user with only access token provided during login can perform operation
"""
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


"""
See All Products Route : Returns a json string which is converted using json.dumps() that converts bson to json
A json string containing all the product details is returned
"""
@app.route("/seeAllProducts", methods=["GET"])
def getAllItems():
    allItems = items.find()
    results = dumps(allItems)
    return results


"""
See Details of Given Product Route : Returns a json string containing details of given product based on product ID
"""
@app.route("/seeAllProducts/<pid>", methods=["GET"])
def getItemDetails(pid):
    item = items.find_one({"_id": ObjectId(pid)})
    result = dumps(item)
    return result


"""
Delete Product of Given Route : Deletes a given product based on product ID
Returns a json string with success method
"""
@app.route("/deleteProduct/<pid>", methods=["DELETE"])
def deleteGivenItem(pid):
    
    result = jsonify("Item with ID {"+str(ObjectId(pid))+"} Deleted Successfully.")
    items.delete_one({"_id": ObjectId(pid)})
    result.status_code = 200

    return result

    
"""
Change Item Detail API route : Used to update the details of items stored in collection
Uses PUT Http request to replace the current details with the newly updated one
Returns a success message
"""
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


        




