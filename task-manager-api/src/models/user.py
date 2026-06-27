"""Model User — definição da entidade, serialização e acesso a dados.

Camada de dados: toda a persistência de usuários mora aqui. Sem HTTP e sem
política de negócio (regras ficam nos controllers).
"""
from werkzeug.security import check_password_hash, generate_password_hash

from src.database import db
from src.time_utils import utcnow


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="user")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        # Nunca serializa o hash da senha.
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "active": self.active,
            "created_at": str(self.created_at),
        }

    def set_password(self, raw_password):
        # Hash forte com salt (PBKDF2 via werkzeug) — substitui o MD5 quebrado.
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def is_admin(self):
        return self.role == "admin"

    # ----- Acesso a dados -----

    @classmethod
    def list_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, user_id):
        return db.session.get(cls, user_id)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

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

    def delete_with_tasks(self):
        """Remove o usuário e suas tasks numa única transação (evita órfãos)."""
        try:
            for task in list(self.tasks):
                db.session.delete(task)
            db.session.delete(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
