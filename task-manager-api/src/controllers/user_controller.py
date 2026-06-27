"""Controller de Usuários — lógica de negócio / casos de uso, incluindo login."""
import logging
import re

from src.constants import (
    DEFAULT_USER_ROLE,
    EMAIL_REGEX,
    MIN_PASSWORD_LENGTH,
    VALID_USER_ROLES,
)
from src.middlewares.error_handler import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from src.models.task import Task
from src.models.user import User

logger = logging.getLogger(__name__)


def list_users():
    result = []
    for user in User.list_all():
        data = user.to_dict()
        data["task_count"] = len(user.tasks)
        result.append(data)
    return result


def get_user(user_id):
    user = _get_user_or_404(user_id)
    data = user.to_dict()
    data["tasks"] = [task.to_dict() for task in Task.for_user(user_id)]
    return data


def create_user(data):
    if not data:
        raise ValidationError("Dados inválidos")

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", DEFAULT_USER_ROLE)

    if not name:
        raise ValidationError("Nome é obrigatório")
    if not email:
        raise ValidationError("Email é obrigatório")
    if not password:
        raise ValidationError("Senha é obrigatória")
    if not _is_valid_email(email):
        raise ValidationError("Email inválido")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError("Senha deve ter no mínimo 4 caracteres")
    if User.get_by_email(email):
        raise ConflictError("Email já cadastrado")
    if role not in VALID_USER_ROLES:
        raise ValidationError("Role inválido")

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role
    user.save()
    logger.info("Usuário criado: %s - %s", user.id, user.name)
    return user.to_dict()


def update_user(user_id, data):
    user = _get_user_or_404(user_id)
    if not data:
        raise ValidationError("Dados inválidos")

    if "name" in data:
        user.name = data["name"]

    if "email" in data:
        if not _is_valid_email(data["email"]):
            raise ValidationError("Email inválido")
        existing = User.get_by_email(data["email"])
        if existing and existing.id != user_id:
            raise ConflictError("Email já cadastrado")
        user.email = data["email"]

    if "password" in data:
        if len(data["password"]) < MIN_PASSWORD_LENGTH:
            raise ValidationError("Senha muito curta")
        user.set_password(data["password"])

    if "role" in data:
        if data["role"] not in VALID_USER_ROLES:
            raise ValidationError("Role inválido")
        user.role = data["role"]

    if "active" in data:
        user.active = data["active"]

    user.save()
    return user.to_dict()


def delete_user(user_id):
    user = _get_user_or_404(user_id)
    user.delete_with_tasks()
    logger.info("Usuário deletado: %s", user_id)
    return {"message": "Usuário deletado com sucesso"}


def get_user_tasks(user_id):
    _get_user_or_404(user_id)
    return [task.to_summary_dict() for task in Task.for_user(user_id)]


def login(data):
    if not data:
        raise ValidationError("Dados inválidos")

    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        raise ValidationError("Email e senha são obrigatórios")

    user = User.get_by_email(email)
    if not user or not user.check_password(password):
        raise UnauthorizedError("Credenciais inválidas")
    if not user.active:
        raise ForbiddenError("Usuário inativo")

    return {
        "message": "Login realizado com sucesso",
        "user": user.to_dict(),
        "token": "fake-jwt-token-" + str(user.id),
    }


# ----- Helpers privados -----


def _get_user_or_404(user_id):
    user = User.get_by_id(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")
    return user


def _is_valid_email(email):
    return re.match(EMAIL_REGEX, email) is not None
