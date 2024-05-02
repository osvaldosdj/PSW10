
FROM python:slim

RUN useradd -ms /bin/bash pythonando

USER pythonando

ENV PYTHONUNBUFFERED 1

WORKDIR /home/pythonando/app

ENV PATH $PATH:/home/pythonando/.local/bin

COPY . /home/pythonando/app/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN python manage.py migrate

ENV DJANGO_SUPERUSER_USERNAME "admin"
ENV DJANGO_SUPERUSER_EMAIL "admin@example.com"
ENV DJANGO_SUPERUSER_PASSWORD "$r-61:k6tP~m"

# Execute o comando para criar o superusuário
RUN python manage.py shell -c "from django.contrib.auth.models import User; \
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')"

# Adiciona o comando para iniciar o Django como ENTRYPOINT
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]