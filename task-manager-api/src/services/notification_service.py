"""Efeitos colaterais isolados: envio de e-mail / notificações.

Mantido como camada de serviço (mockável) para que, quando os controllers
precisarem notificar, a regra de negócio não conheça o canal de entrega. As
credenciais SMTP vêm da configuração (ambiente), nunca hardcoded.
"""
import logging
import smtplib

from src.config.settings import settings
from src.time_utils import utcnow

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.notifications = []
        self.email_host = settings.SMTP_HOST
        self.email_port = settings.SMTP_PORT
        self.email_user = settings.SMTP_USER
        self.email_password = settings.SMTP_PASSWORD

    def send_email(self, to, subject, body):
        if not self.email_user or not self.email_password:
            logger.warning(
                "SMTP não configurado; e-mail para %s não enviado.", to
            )
            return False
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_user, to, message)
            server.quit()
            logger.info("E-mail enviado para %s", to)
            return True
        except Exception as error:
            logger.error("Erro ao enviar e-mail: %s", error)
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\n"
            f"A task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append(
            {
                "type": "task_assigned",
                "user_id": user.id,
                "task_id": task.id,
                "timestamp": utcnow(),
            }
        )

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = (
            f"Olá {user.name},\n\n"
            f"A task '{task.title}' está atrasada!\n\n"
            f"Data limite: {task.due_date}"
        )
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n["user_id"] == user_id]
