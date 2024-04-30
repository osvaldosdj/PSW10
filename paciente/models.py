from django.db import models
from django.contrib.auth.models import User
from medico.models import DatasAbertas, DadosMedico
from datetime import datetime, timedelta

#from paciente.views import consulta

# Create your models here.

class Consulta(models.Model):
    status_choices = (
        ('A', 'Agendada'),
        ('F', 'Finalizada'),
        ('C', 'Cancelada'),
        ('I', 'Iniciada')

    )

    pagto_status_choices = (
        ('S', 'Sim'),
        ('N', 'Não'),
        
    )

    paciente = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    data_aberta = models.ForeignKey(DatasAbertas, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=1, choices=status_choices, default='A')
    link = models.URLField(null=True, blank=True)
    status_pagto = models.CharField(max_length=1, choices=pagto_status_choices, default='N')

    @property
    def diferenca_dias(self):
        try:
            diferenca = (self.data_aberta.data.date() - datetime.now().date()).days
            return diferenca
        except AttributeError:
            return None
    
    def __str__(self):
        return self.paciente.username

class Documento(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=30)
    documento = models.FileField(upload_to='documentos')

    def __str__(self):
        return self.titulo
    
class Observacoes(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.DO_NOTHING)
    observacao = models.TextField( blank=True)
    

    def __str__(self):
        return self.observacao