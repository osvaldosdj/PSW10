#!/bin/bash

# Extrair variáveis de ambiente do arquivo .env
source .env

# Executar o comando para criar o superusuário
python manage.py shell -c "from django.contrib.auth.models import User; \
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')"

# Iniciar o servidor Django
exec "$@"
