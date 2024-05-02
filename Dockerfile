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

RUN python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL --password DJANGO_SUPERUSER_PASSWORD

# Adiciona o comando para iniciar o Django como ENTRYPOINT
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]