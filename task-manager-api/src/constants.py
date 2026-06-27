"""Constantes de domínio — substituem magic numbers/strings espalhados no código."""

# Status de tasks
VALID_TASK_STATUSES = ["pending", "in_progress", "done", "cancelled"]
TERMINAL_TASK_STATUSES = ["done", "cancelled"]
DEFAULT_TASK_STATUS = "pending"

# Papéis de usuário
VALID_USER_ROLES = ["user", "admin", "manager"]
DEFAULT_USER_ROLE = "user"

# Regras de título
MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200

# Regras de prioridade
MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3

# Regras de senha
MIN_PASSWORD_LENGTH = 4

# Categoria
DEFAULT_CATEGORY_COLOR = "#000000"

# Formatos / validação
DATE_FORMAT = "%Y-%m-%d"
EMAIL_REGEX = r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"

# Janela de atividade recente nos relatórios (dias)
RECENT_ACTIVITY_DAYS = 7
