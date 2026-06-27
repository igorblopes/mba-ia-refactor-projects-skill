"""Controller de Relatórios — agregações e produtividade.

Carrega as tasks uma única vez (eager-loaded) e calcula tudo em memória,
eliminando as queries N+1 que existiam ao iterar usuários/tasks.
"""
from datetime import timedelta

from src.constants import RECENT_ACTIVITY_DAYS, VALID_TASK_STATUSES
from src.metrics import completion_rate
from src.middlewares.error_handler import NotFoundError
from src.models.category import Category
from src.models.task import Task
from src.models.user import User
from src.time_utils import utcnow

HIGH_PRIORITY_THRESHOLD = 2


def summary():
    tasks = Task.list_all()
    users = User.list_all()
    now = utcnow()
    recent_cutoff = now - timedelta(days=RECENT_ACTIVITY_DAYS)

    status_counts = {status: 0 for status in VALID_TASK_STATUSES}
    priority_counts = {priority: 0 for priority in range(1, 6)}
    overdue_list = []
    recent_created = 0
    recent_done = 0
    per_user = {}

    for task in tasks:
        if task.status in status_counts:
            status_counts[task.status] += 1
        if task.priority in priority_counts:
            priority_counts[task.priority] += 1
        if task.is_overdue():
            overdue_list.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "due_date": str(task.due_date),
                    "days_overdue": (now - task.due_date).days,
                }
            )
        if task.created_at and task.created_at >= recent_cutoff:
            recent_created += 1
        if task.status == "done" and task.updated_at and task.updated_at >= recent_cutoff:
            recent_done += 1

        bucket = per_user.setdefault(task.user_id, {"total": 0, "done": 0})
        bucket["total"] += 1
        if task.status == "done":
            bucket["done"] += 1

    user_stats = []
    for user in users:
        bucket = per_user.get(user.id, {"total": 0, "done": 0})
        total = bucket["total"]
        done = bucket["done"]
        user_stats.append(
            {
                "user_id": user.id,
                "user_name": user.name,
                "total_tasks": total,
                "completed_tasks": done,
                "completion_rate": completion_rate(done, total),
            }
        )

    return {
        "generated_at": str(now),
        "overview": {
            "total_tasks": len(tasks),
            "total_users": len(users),
            "total_categories": Category.count(),
        },
        "tasks_by_status": {
            "pending": status_counts["pending"],
            "in_progress": status_counts["in_progress"],
            "done": status_counts["done"],
            "cancelled": status_counts["cancelled"],
        },
        "tasks_by_priority": {
            "critical": priority_counts[1],
            "high": priority_counts[2],
            "medium": priority_counts[3],
            "low": priority_counts[4],
            "minimal": priority_counts[5],
        },
        "overdue": {
            "count": len(overdue_list),
            "tasks": overdue_list,
        },
        "recent_activity": {
            "tasks_created_last_7_days": recent_created,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_stats,
    }


def user_report(user_id):
    user = User.get_by_id(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")

    tasks = Task.for_user(user_id)
    total = len(tasks)

    status_counts = {
        "done": 0,
        "pending": 0,
        "in_progress": 0,
        "cancelled": 0,
    }
    overdue = 0
    high_priority = 0
    for task in tasks:
        if task.status in status_counts:
            status_counts[task.status] += 1
        if task.priority <= HIGH_PRIORITY_THRESHOLD:
            high_priority += 1
        if task.is_overdue():
            overdue += 1

    done = status_counts["done"]
    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
        "statistics": {
            "total_tasks": total,
            "done": done,
            "pending": status_counts["pending"],
            "in_progress": status_counts["in_progress"],
            "cancelled": status_counts["cancelled"],
            "overdue": overdue,
            "high_priority": high_priority,
            "completion_rate": completion_rate(done, total),
        },
    }
