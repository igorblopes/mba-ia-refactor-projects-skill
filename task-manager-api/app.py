"""Ponto de entrada — cria a app via factory e a sobe com config do ambiente."""
from src.app import create_app
from src.config.settings import settings

app = create_app()

if __name__ == "__main__":
    app.run(debug=settings.DEBUG, host=settings.HOST, port=settings.PORT)
