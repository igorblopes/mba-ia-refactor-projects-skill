"""Script para popular o banco com dados iniciais."""
from datetime import timedelta

from app import app
from src.database import db
from src.models import Category, Task, User
from src.time_utils import utcnow


def seed_data():
    with app.app_context():
        Task.query.delete()
        User.query.delete()
        Category.query.delete()
        db.session.commit()

        users = [
            ("João Silva", "joao@email.com", "1234", "admin"),
            ("Maria Santos", "maria@email.com", "abcd", "user"),
            ("Pedro Oliveira", "pedro@email.com", "pass", "manager"),
        ]
        user_objs = []
        for name, email, password, role in users:
            user = User()
            user.name = name
            user.email = email
            user.set_password(password)
            user.role = role
            db.session.add(user)
            user_objs.append(user)
        db.session.commit()

        categories = [
            ("Backend", "Tarefas de backend", "#3498db"),
            ("Frontend", "Tarefas de frontend", "#2ecc71"),
            ("DevOps", "Tarefas de infraestrutura", "#e74c3c"),
            ("Bug", "Correção de bugs", "#e67e22"),
        ]
        category_objs = []
        for name, description, color in categories:
            category = Category()
            category.name = name
            category.description = description
            category.color = color
            db.session.add(category)
            category_objs.append(category)
        db.session.commit()

        u1, u2, u3 = user_objs
        c1, c2, c3, c4 = category_objs

        tasks_data = [
            {"title": "Implementar autenticação JWT", "description": "Adicionar autenticação real com JWT", "status": "pending", "priority": 1, "user_id": u1.id, "category_id": c1.id, "due_date": utcnow() - timedelta(days=3)},
            {"title": "Criar tela de login", "description": "Tela de login responsiva", "status": "in_progress", "priority": 2, "user_id": u2.id, "category_id": c2.id, "due_date": utcnow() + timedelta(days=5)},
            {"title": "Configurar CI/CD", "description": "Pipeline com GitHub Actions", "status": "done", "priority": 2, "user_id": u3.id, "category_id": c3.id, "tags": "devops,ci,github"},
            {"title": "Corrigir bug no filtro de busca", "description": "Filtro não funciona com caracteres especiais", "status": "pending", "priority": 1, "user_id": u1.id, "category_id": c4.id, "due_date": utcnow() - timedelta(days=1)},
            {"title": "Adicionar paginação na API", "description": "Endpoints retornam todos os registros", "status": "pending", "priority": 3, "user_id": u1.id, "category_id": c1.id, "due_date": utcnow() + timedelta(days=10)},
            {"title": "Escrever testes unitários", "description": "Cobertura mínima de 80%", "status": "pending", "priority": 2, "user_id": u2.id, "category_id": c1.id},
            {"title": "Documentar API com Swagger", "description": "Gerar documentação automática", "status": "cancelled", "priority": 4, "user_id": u3.id, "category_id": c1.id},
            {"title": "Refatorar models", "description": "Melhorar organização dos models", "status": "in_progress", "priority": 3, "user_id": u2.id, "category_id": c1.id, "tags": "refactor,tech-debt"},
            {"title": "Configurar monitoramento", "description": "Prometheus + Grafana", "status": "pending", "priority": 4, "user_id": u3.id, "category_id": c3.id, "due_date": utcnow() + timedelta(days=20)},
            {"title": "Melhorar validações de input", "description": "Usar marshmallow ou pydantic", "status": "pending", "priority": 3, "user_id": u1.id, "category_id": c1.id, "tags": "improvement,validation"},
        ]

        for item in tasks_data:
            task = Task()
            task.title = item["title"]
            task.description = item["description"]
            task.status = item["status"]
            task.priority = item["priority"]
            task.user_id = item["user_id"]
            task.category_id = item["category_id"]
            if "due_date" in item:
                task.due_date = item["due_date"]
            if "tags" in item:
                task.tags = item["tags"]
            db.session.add(task)

        db.session.commit()
        print("Seed concluído com sucesso!")
        print(f"  {User.count()} usuários")
        print(f"  {Category.count()} categorias")
        print(f"  {Task.query.count()} tasks")


if __name__ == "__main__":
    seed_data()
