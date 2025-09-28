#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate 
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza

# --- Database config ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False 

db.init_app(app)
migrate = Migrate(app, db) 
api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([r.to_dict(only=("id", "name", "address")) for r in restaurants])


# GET /restaurants/<id>
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    return jsonify(restaurant.to_dict())


# DELETE /restaurants/<id>
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    db.session.delete(restaurant)
    db.session.commit()
    return "", 204


# GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([p.to_dict(only=("id", "name", "ingredients")) for p in pizzas])


# POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    try:
        new_rp = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"],
        )
        db.session.add(new_rp)
        db.session.commit()
        return jsonify(new_rp.to_dict()), 201
    except Exception as e:
        # Handle validation errors (like invalid price)
        return jsonify({"errors": ["validation errors"]}), 400


if __name__ == "__main__":
    app.run(port=5555, debug=True) 