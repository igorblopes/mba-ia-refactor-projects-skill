"""Camada HTTP fina de Categorias."""
from flask import Blueprint, jsonify, request

from src.controllers import category_controller

category_bp = Blueprint("categories", __name__)


@category_bp.route("/categories", methods=["GET"])
def get_categories():
    return jsonify(category_controller.list_categories()), 200


@category_bp.route("/categories", methods=["POST"])
def create_category():
    body = request.get_json(silent=True)
    return jsonify(category_controller.create_category(body)), 201


@category_bp.route("/categories/<int:cat_id>", methods=["PUT"])
def update_category(cat_id):
    body = request.get_json(silent=True)
    return jsonify(category_controller.update_category(cat_id, body)), 200


@category_bp.route("/categories/<int:cat_id>", methods=["DELETE"])
def delete_category(cat_id):
    return jsonify(category_controller.delete_category(cat_id)), 200
