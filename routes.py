from flask import Blueprint, request, jsonify, render_template
from models import db, Recipe, Ingredient, RecipeIngredient
from werkzeug.exceptions import BadRequest

bp = Blueprint("main", __name__)

@bp.route("/")
def home():
    return render_template("index.html")

@bp.route("/add", methods=["POST"])
def add_recipe():
    data = request.json

    if not all(key in data for key in ["title", "ingredients"]):
        raise BadRequest("Missing required fields")

    recipe = Recipe(
        title=data["title"],
        description=data.get("description", ""),
        servings=data.get("servings", 1)
    )

    db.session.add(recipe)
    db.session.flush()

    for ing in data.get("ingredients", []):
        if not all(key in ing for key in ["name", "amount", "unit"]):
            raise BadRequest("Invalid ingredient format")

        ingredient = Ingredient.query.filter_by(name=ing["name"]).first()

        if not ingredient:
            ingredient = Ingredient(name=ing["name"])
            db.session.add(ingredient)
            db.session.flush()

        ri = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            amount=ing["amount"],
            unit=ing["unit"]
        )
        db.session.add(ri)

    db.session.commit()
    return jsonify({"status": "ok"})

@bp.route("/recipes")
def get_recipes():
    return jsonify(format_recipes(Recipe.query.all()))

@bp.route("/recipes/<letter>")
def get_by_letter(letter):
    recipes = Recipe.query.filter(
        Recipe.title.ilike(f"{letter}%")
    ).all()

    return jsonify(format_recipes(recipes))

def format_recipes(recipes):
    result = []
    for r in recipes:
        result.append({
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "servings": r.servings,
            "ingredients": [
                {
                    "name": ri.ingredient.name,
                    "amount": ri.amount,
                    "unit": ri.unit
                } for ri in r.ingredients
            ]
        })
    return result

@bp.route("/update/<int:id>", methods=["PUT"])
def update_recipe(id):
    data = request.json

    if not all(key in data for key in ["title", "ingredients"]):
        raise BadRequest("Missing required fields")

    recipe = Recipe.query.get_or_404(id)

    recipe.title = data["title"]
    recipe.description = data.get("description", "")
    recipe.servings = data.get("servings", 1)

    # Delete existing ingredients
    RecipeIngredient.query.filter_by(recipe_id=id).delete()

    for ing in data.get("ingredients", []):
        if not all(key in ing for key in ["name", "amount", "unit"]):
            raise BadRequest("Invalid ingredient format")

        ingredient = Ingredient.query.filter_by(name=ing["name"]).first()

        if not ingredient:
            ingredient = Ingredient(name=ing["name"])
            db.session.add(ingredient)
            db.session.flush()

        ri = RecipeIngredient(
            recipe_id=id,
            ingredient_id=ingredient.id,
            amount=ing["amount"],
            unit=ing["unit"]
        )
        db.session.add(ri)

    db.session.commit()
    return {"status": "updated"}

@bp.route("/delete/<int:id>", methods=["DELETE"])
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)

    db.session.delete(recipe)
    db.session.commit()

    return {"status": "deleted"}

@bp.route("/search", methods=["GET"])  # Ensure this route is added to the blueprint
def search_recipes():
    query = request.args.get("query", "")
    recipes = Recipe.query.filter(
        Recipe.title.ilike(f"%{query}%")
    ).all()

    return jsonify(format_recipes(recipes))