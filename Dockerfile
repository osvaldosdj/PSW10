# Use a imagem base do Python
FROM python:3.9

# Defina a variável de ambiente DJANGO_SETTINGS_MODULE
ENV DJANGO_SETTINGS_MODULE "seu_projeto.settings"

# Instalação das dependências do projeto
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copie o restante do seu projeto para dentro do contêiner
COPY . /app

# Defina o diretório de trabalho como o diretório do seu projeto
WORKDIR /app

# Use os secrets do GitHub para definir as variáveis de ambiente
ENV DJANGO_SUPERUSER_USERNAME ${{ secrets.DJANGO_SUPERUSER_USERNAME }}
ENV DJANGO_SUPERUSER_EMAIL ${{ secrets.DJANGO_SUPERUSER_EMAIL }}
ENV DJANGO_SUPERUSER_PASSWORD ${{ secrets.DJANGO_SUPERUSER_PASSWORD }}

# Execute o comando para criar o superusuário
RUN python manage.py shell -c "from django.contrib.auth.models import User; \
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')"

# Exponha a porta onde a sua aplicação estará rodando
EXPOSE 8000

# Comando para iniciar o servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
