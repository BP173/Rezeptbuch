from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.Text)
    servings = db.Column(db.Integer, default=1)

    ingredients = db.relationship(
        "RecipeIngredient",
        backref="recipe",
        cascade="all, delete-orphan"
    )

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, index=True)

class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredients'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), index=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), index=True)
    amount = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)

    ingredient = db.relationship("Ingredient")