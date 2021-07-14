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

app = Flask(__name__)
jwt = JWTManager(app)

app.config["JWT_SECRET_KEY"] = "ACCESS_KEY_999"


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
    # _json = request.json

    # if request.is_json:
    #     user_email = _json["email"]
    #     user_password = _json["password"]
    #     hash_password = generate_password_hash(user_password)
    
    # print(hash_password)
    # is_present = zhiffy.find_one({"email": user_email, "password": hash_password})

    # if is_present:
    #     user_access_token = create_access_token(identity=user_email)
    #     return jsonify(message="Voila! User Successfully Logged In.", access_token=user_access_token)
    # else:
    #     return jsonify(message="Wrong Credentials. Please Retry."), 401
    _json = request.json
    user_email = _json["email"]
    user_password = _json["password"]

    current_user = zhiffy.find_one({'email': user_email})

    if current_user:
        if bcrypt.hashpw(user_password.encode('utf-8'), current_user["password"]) == current_user["password"]:
            user_access_token = create_access_token(identity=user_email)
            return jsonify(message="Voila! User Successfully Logged In.", access_token=user_access_token)

    return "Invalid Credentials. Please Retry."


if __name__ == '__main__':
    app.run(host="localhost", debug=True)


        




