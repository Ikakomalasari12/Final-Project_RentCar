from flask import Flask, request, render_template, redirect, url_for, jsonify, make_response, current_app
from pymongo import MongoClient
import requests
import hashlib
from datetime import datetime
from bson import ObjectId
import os
import jwt
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from os.path import join, dirname
from dotenv import load_dotenv
from babel.numbers import format_currency

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# MONGODB_URI = os.environ.get("MONGODB_URI")
# DB_NAME =  os.environ.get("DB_NAME")

MONGODB_CONNECTION_STRING = 'mongodb+srv://root:root@root.37wyvzm.mongodb.net/'
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.rentcar
# client = MongoClient(MONGODB_URI)
# db = client[DB_NAME]

app = Flask(__name__)

SECRET_KEY = 'secret0'
TOKEN_KEY = 'mytoken'


@app.route('/', methods = ['GET'])
def main():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload =jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        print(user_info)
        return render_template('home.html', user_info=user_info, logged_in = logged_in, is_admin = is_admin)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('home.html', msg=msg)

@app.route('/signup')
def signup():
    return render_template('register.html')

@app.route('/sign_up/save', methods = ['POST'])
def sign_up():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    password_hash = hashlib.sha256(password. encode('utf-8')).hexdigest()
    doc = {
        "name" : name,
        "email" : email,
        "category" : 'visitor',
        "password" : password_hash                                          
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/signin')
def signin():
    return render_template('login.html')

@app.route('/sign_in', methods=['POST'])
def sign_in():
    email = request.form["email"]
    password = request.form["password"]
    print(email)
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    print(pw_hash)
    result = db.users.find_one(
        {
            "email": email,
            "password": pw_hash,
        }
    )
    if result:
        payload = {
            "id": email,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )

@app.route('/syarat&ketentuan')
def syaratketentuan():
    return render_template('syarat&ketentuan.html')



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)