"""Controller de Tasks — lógica de negócio / casos de uso.

Recebe dados já parseados pelas views, aplica as regras, orquestra os models e
devolve dicts simples (ou levanta erros de domínio). Não conhece `request`/`jsonify`.
"""
import logging
from datetime import datetime

from src.constants import (
    DATE_FORMAT,
    DEFAULT_PRIORITY,
    DEFAULT_TASK_STATUS,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    VALID_TASK_STATUSES,
)
from src.metrics import completion_rate
from src.middlewares.error_handler import NotFoundError, ValidationError
from src.models.category import Category
from src.models.task import Task
from src.models.user import User

logger = logging.getLogger(__name__)


def list_tasks():
    tasks = Task.list_all()
    return [
        task.to_dict(include_overdue=True, include_relations=True)
        for task in tasks
    ]


def get_task(task_id):
    task = _get_task_or_404(task_id)
    return task.to_dict(include_overdue=True)


def create_task(data):
    if not data:
        raise ValidationError("Dados inválidos")

    title = data.get("title")
    _validate_required_title(title)

    status = data.get("status", DEFAULT_TASK_STATUS)
    priority = data.get("priority", DEFAULT_PRIORITY)
    _validate_status(status)
    _validate_priority(priority)

    user_id = data.get("user_id")
    category_id = data.get("category_id")
    _ensure_user_exists(user_id)
    _ensure_category_exists(category_id)

    task = Task()
    task.title = title
    task.description = data.get("description", "")
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    due_date = data.get("due_date")
    if due_date:
        task.due_date = _parse_due_date(
            due_date, "Formato de data inválido. Use YYYY-MM-DD"
        )

    tags = data.get("tags")
    if tags:
        task.tags = _join_tags(tags)

    task.save()
    logger.info("Task criada: %s - %s", task.id, task.title)
    return task.to_dict()


def update_task(task_id, data):
    task = _get_task_or_404(task_id)
    if not data:
        raise ValidationError("Dados inválidos")

    if "title" in data:
        _validate_title_length(data["title"])
        task.title = data["title"]

    if "description" in data:
        task.description = data["description"]

    if "status" in data:
        _validate_status(data["status"])
        task.status = data["status"]

    if "priority" in data:
        _validate_priority(data["priority"])
        task.priority = data["priority"]

    if "user_id" in data:
        _ensure_user_exists(data["user_id"])
        task.user_id = data["user_id"]

    if "category_id" in data:
        _ensure_category_exists(data["category_id"])
        task.category_id = data["category_id"]

    if "due_date" in data:
        if data["due_date"]:
            task.due_date = _parse_due_date(
                data["due_date"], "Formato de data inválido"
            )
        else:
            task.due_date = None

    if "tags" in data:
        task.tags = _join_tags(data["tags"])

    task.touch()
    task.save()
    logger.info("Task atualizada: %s", task.id)
    return task.to_dict()


def delete_task(task_id):
    task = _get_task_or_404(task_id)
    task.delete()
    logger.info("Task deletada: %s", task_id)
    return {"message": "Task deletada com sucesso"}


def search_tasks(params):
    query = params.get("q", "") or None
    status = params.get("status", "") or None
    priority = _to_int_or_none(params.get("priority", ""), "Prioridade inválida")
    user_id = _to_int_or_none(params.get("user_id", ""), "Usuário inválido")

    tasks = Task.search(
        query=query, status=status, priority=priority, user_id=user_id
    )
    return [task.to_dict() for task in tasks]


def task_stats():
    tasks = Task.list_all()
    total = len(tasks)

    counts = {status: 0 for status in VALID_TASK_STATUSES}
    overdue = 0
    for task in tasks:
        if task.status in counts:
            counts[task.status] += 1
        if task.is_overdue():
            overdue += 1

    done = counts["done"]
    return {
        "total": total,
        "pending": counts["pending"],
        "in_progress": counts["in_progress"],
        "done": done,
        "cancelled": counts["cancelled"],
        "overdue": overdue,
        "completion_rate": completion_rate(done, total),
    }


# ----- Helpers privados -----


def _get_task_or_404(task_id):
    task = Task.get_by_id(task_id)
    if not task:
        raise NotFoundError("Task não encontrada")
    return task


def _validate_required_title(title):
    if not title:
        raise ValidationError("Título é obrigatório")
    _validate_title_length(title)


def _validate_title_length(title):
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError("Título muito curto")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError("Título muito longo")


def _validate_status(status):
    if status not in VALID_TASK_STATUSES:
        raise ValidationError("Status inválido")


def _validate_priority(priority):
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise ValidationError("Prioridade deve ser entre 1 e 5")


def _ensure_user_exists(user_id):
    if user_id and not User.get_by_id(user_id):
        raise NotFoundError("Usuário não encontrado")


def _ensure_category_exists(category_id):
    if category_id and not Category.get_by_id(category_id):
        raise NotFoundError("Categoria não encontrada")


def _parse_due_date(value, error_message):
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except (ValueError, TypeError):
        raise ValidationError(error_message)


def _join_tags(tags):
    if isinstance(tags, list):
        return ",".join(tags)
    return tags


def _to_int_or_none(raw, error_message):
    if raw is None or raw == "":
        return None
    try:
        return int(raw)
    except (ValueError, TypeError):
        raise ValidationError(error_message)
