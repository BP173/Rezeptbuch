from functools import wraps

from flask import Blueprint, request, jsonify, render_template, session, current_app
import models
db = models.db
Recipe = models.Recipe
Ingredient = models.Ingredient
RecipeIngredient = models.RecipeIngredient
from werkzeug.exceptions import BadRequest

bp = Blueprint("main", __name__)

ADMIN_SESSION_KEY = "admin_ok"


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get(ADMIN_SESSION_KEY):
            return jsonify({"error": "Unauthorized", "status": "unauthorized"}), 401
        return view(*args, **kwargs)
    return wrapped


def api_key_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        expected_key = current_app.config.get("API_ADD_KEY", "")
        if not expected_key:
            return jsonify({"error": "API key not configured", "status": "misconfigured"}), 503

        provided_key = request.headers.get("X-API-Key", "")
        if not provided_key:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                provided_key = auth_header.split(" ", 1)[1].strip()

        if provided_key != expected_key:
            return jsonify({"error": "Unauthorized", "status": "unauthorized"}), 401
        return view(*args, **kwargs)
    return wrapped


def create_recipe_from_payload(data):
    if not isinstance(data, dict):
        raise BadRequest("Invalid JSON payload")

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
    return recipe


@bp.route("/")
def home():
    return render_template("index.html")


@bp.route("/admin/status", methods=["GET"])
def admin_status():
    return jsonify({"authenticated": bool(session.get(ADMIN_SESSION_KEY))})


@bp.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")
    expected = current_app.config.get("ADMIN_PASSWORD") or ""
    if password and password == expected:
        session[ADMIN_SESSION_KEY] = True
        session.permanent = True
        return jsonify({"status": "ok"})
    return jsonify({"error": "Invalid password"}), 401


@bp.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.pop(ADMIN_SESSION_KEY, None)
    return jsonify({"status": "ok"})


@bp.route("/add", methods=["POST"])
@admin_required
def add_recipe():
    data = request.get_json(silent=True)
    recipe = create_recipe_from_payload(data)
    return jsonify({"status": "ok", "id": recipe.id})


@bp.route("/api/add", methods=["POST"])
@api_key_required
def api_add_recipe():
    data = request.get_json(silent=True)
    recipe = create_recipe_from_payload(data)
    return jsonify({"status": "ok", "id": recipe.id})

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
@admin_required
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
    return jsonify({"status": "updated"})

@bp.route("/delete/<int:id>", methods=["DELETE"])
@admin_required
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)

    db.session.delete(recipe)
    db.session.commit()

    return jsonify({"status": "deleted"})

@bp.route("/search", methods=["GET"])  # Ensure this route is added to the blueprint
def search_recipes():
    query = request.args.get("query", "")
    recipes = Recipe.query.filter(
        Recipe.title.ilike(f"%{query}%")
    ).all()

    return jsonify(format_recipes(recipes))

@bp.route('/recipe/<int:id>')
def get_recipe(id):
    try:
        recipe = db.session.query(Recipe).filter_by(id=id).first()
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        
        return jsonify({
            'id': recipe.id,
            'title': recipe.title,
            'description': recipe.description,
            'servings': recipe.servings,
            'ingredients': [
                {
                    'id': ing.id,
                    'name': ing.ingredient.name,
                    'amount': ing.amount,
                    'unit': ing.unit
                }
                for ing in recipe.ingredients
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500