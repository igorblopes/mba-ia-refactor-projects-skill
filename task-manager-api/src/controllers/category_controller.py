"""Controller de Categorias — lógica de negócio / casos de uso."""
import logging

from src.constants import DEFAULT_CATEGORY_COLOR
from src.middlewares.error_handler import NotFoundError, ValidationError
from src.models.category import Category
from src.models.task import Task

logger = logging.getLogger(__name__)


def list_categories():
    counts = Task.count_by_category()
    result = []
    for category in Category.list_all():
        data = category.to_dict()
        data["task_count"] = counts.get(category.id, 0)
        result.append(data)
    return result


def create_category(data):
    if not data:
        raise ValidationError("Dados inválidos")

    name = data.get("name")
    if not name:
        raise ValidationError("Nome é obrigatório")

    category = Category()
    category.name = name
    category.description = data.get("description", "")
    category.color = data.get("color", DEFAULT_CATEGORY_COLOR)
    category.save()
    return category.to_dict()


def update_category(category_id, data):
    category = _get_category_or_404(category_id)
    data = data or {}

    if "name" in data:
        category.name = data["name"]
    if "description" in data:
        category.description = data["description"]
    if "color" in data:
        category.color = data["color"]

    category.save()
    return category.to_dict()


def delete_category(category_id):
    category = _get_category_or_404(category_id)
    category.delete_with_task_cleanup()
    return {"message": "Categoria deletada"}


# ----- Helpers privados -----


def _get_category_or_404(category_id):
    category = Category.get_by_id(category_id)
    if not category:
        raise NotFoundError("Categoria não encontrada")
    return category
