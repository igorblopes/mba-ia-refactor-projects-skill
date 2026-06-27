"""Model Task — definição da entidade, serialização, predicados de domínio e
acesso a dados.

A regra "uma task está atrasada?" vive aqui (`is_overdue`) como única fonte de
verdade, eliminando o bloco duplicado que existia em 7 lugares.
"""
from sqlalchemy.orm import joinedload

from src.constants import (
    DEFAULT_PRIORITY,
    DEFAULT_TASK_STATUS,
    MAX_PRIORITY,
    MIN_PRIORITY,
    TERMINAL_TASK_STATUSES,
    VALID_TASK_STATUSES,
)
from src.database import db
from src.time_utils import utcnow


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=DEFAULT_TASK_STATUS)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=True
    )
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship("User", backref="tasks")
    category = db.relationship("Category", backref="tasks")

    # ----- Serialização -----

    def to_dict(self, include_overdue=False, include_relations=False):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "due_date": str(self.due_date) if self.due_date else None,
            "tags": self.tags.split(",") if self.tags else [],
        }
        if include_overdue:
            data["overdue"] = self.is_overdue()
        if include_relations:
            data["user_name"] = self.user.name if self.user else None
            data["category_name"] = (
                self.category.name if self.category else None
            )
        return data

    def to_summary_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_at": str(self.created_at),
            "due_date": str(self.due_date) if self.due_date else None,
            "overdue": self.is_overdue(),
        }

    # ----- Predicados de domínio -----

    def is_overdue(self):
        return bool(
            self.due_date
            and self.due_date < utcnow()
            and self.status not in TERMINAL_TASK_STATUSES
        )

    @staticmethod
    def is_valid_status(status):
        return status in VALID_TASK_STATUSES

    @staticmethod
    def is_valid_priority(priority):
        return MIN_PRIORITY <= priority <= MAX_PRIORITY

    # ----- Acesso a dados -----

    @classmethod
    def list_all(cls):
        """Lista todas as tasks com user e category carregados (evita N+1)."""
        return (
            cls.query.options(
                joinedload(cls.user), joinedload(cls.category)
            ).all()
        )

    @classmethod
    def get_by_id(cls, task_id):
        return db.session.get(cls, task_id)

    @classmethod
    def for_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def search(cls, query=None, status=None, priority=None, user_id=None):
        q = cls.query
        if query:
            q = q.filter(
                db.or_(
                    cls.title.like(f"%{query}%"),
                    cls.description.like(f"%{query}%"),
                )
            )
        if status:
            q = q.filter(cls.status == status)
        if priority is not None:
            q = q.filter(cls.priority == priority)
        if user_id is not None:
            q = q.filter(cls.user_id == user_id)
        return q.all()

    @classmethod
    def count_by_category(cls):
        """Contagem de tasks por categoria numa única query (evita N+1)."""
        rows = (
            db.session.query(cls.category_id, db.func.count(cls.id))
            .group_by(cls.category_id)
            .all()
        )
        return {category_id: total for category_id, total in rows}

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception:
            db.session.rollback()
            raise

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def touch(self):
        self.updated_at = utcnow()
