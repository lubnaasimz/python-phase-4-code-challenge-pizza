from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# keep consistent FK naming for migrations
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # One-to-many: a Restaurant has many RestaurantPizza rows
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )

    # Many-to-many shortcut (via association table RestaurantPizza)
    pizzas = association_proxy("restaurant_pizzas", "pizza")

    # Serializer rules: when serializing Restaurant, include restaurant_pizzas
    # but prevent each restaurant_pizza from again serializing the parent restaurant
    serialize_rules = ("-restaurant_pizzas.restaurant",)

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # One-to-many: a Pizza has many RestaurantPizza rows
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="pizza",
        cascade="all, delete-orphan"
    )

    # Many-to-many shortcut (via association table RestaurantPizza)
    restaurants = association_proxy("restaurant_pizzas", "restaurant")

    # Serializer rules: prevent recursion by not having each restaurant_pizza re-serialize pizza
    serialize_rules = ("-restaurant_pizzas.pizza",)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Foreign keys linking to restaurants and pizzas
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"))

    # Relationships back to parent records (allow python-level navigation)
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")

    # Serializer rules: include pizza and restaurant, but avoid recursive backrefs
    serialize_rules = ("-restaurant.restaurant_pizzas", "-pizza.restaurant_pizzas")

    # Validation: price must be between 1 and 30 (inclusive)
    @validates("price")
    def validate_price(self, key, value):
        if value is None:
            raise ValueError("price must be present")
        if not isinstance(value, int):
            raise ValueError("price must be an integer")
        if value < 1 or value > 30:
            raise ValueError("price must be between 1 and 30")
        return value

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>" 
