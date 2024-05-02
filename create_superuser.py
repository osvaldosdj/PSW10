import os
import sys
import django
from django.contrib.auth.models import User

def create_superuser(username, email, password):
    try:
        # Configuração do Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seu_projeto.settings')
        django.setup()

        # Criação do superusuário
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            print("Superusuário criado com sucesso!")
        else:
            print("O superusuário já existe.")
    except Exception as e:
        print(f"Erro ao criar superusuário: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Obtendo informações do .env
    username = os.getenv("DJANGO_SUPERUSER_USERNAME")
    email = os.getenv("DJANGO_SUPERUSER_EMAIL")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

    if not all([username, email, password]):
        print("As variáveis de ambiente necessárias não estão definidas.")
        sys.exit(1)

    create_superuser(username, email, password)
