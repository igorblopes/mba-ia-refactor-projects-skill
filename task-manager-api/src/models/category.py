"""Model Category — definição da entidade, serialização e acesso a dados."""
from src.database import db
from src.time_utils import utcnow


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(7), default="#000000")
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "created_at": str(self.created_at),
        }

    # ----- Acesso a dados -----

    @classmethod
    def list_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, category_id):
        return db.session.get(cls, category_id)

    @classmethod
    def count(cls):
        return cls.query.count()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception:
            db.session.rollback()
            raise

    def delete_with_task_cleanup(self):
        """Remove a categoria desvinculando as tasks numa única transação.

        Evita `category_id` órfão apontando para uma categoria inexistente.
        """
        try:
            for task in list(self.tasks):
                task.category_id = None
            db.session.delete(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
