from datetime import datetime, timedelta
from django.shortcuts import redirect, render
from medico.models import DadosMedico, DatasAbertas, Especialidades, is_medico
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.contrib import messages
from paciente.models import Consulta, Documento

# Create your views here.

@login_required
def home(request):
    if request.method == "GET":
        medicos = DadosMedico.objects.all()
        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')
        minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
        
        #print(minhas_consultas)
        if medico_filtrar:
            medicos = medicos.filter(nome__icontains = medico_filtrar)

        if especialidades_filtrar:
            medicos = medicos.filter(especialidade_id__in=especialidades_filtrar)
            
        especialidades = Especialidades.objects.all()
        return render(request, 'home.html', {'minhas_consultas': minhas_consultas, 'medicos': medicos, 'especialidades': especialidades, 'is_medico': is_medico(request.user) })
        

@login_required
def escolher_horario(request, id_dados_medicos):
    if request.method == "GET":
        medico = DadosMedico.objects.get(id=id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(agendado=False)
        return render(request, 'escolher_horario.html', {'medico': medico, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})
    

@login_required
def agendar_horario(request, id_data_aberta):
    if request.method == "GET":
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)

        horario_agendado = Consulta(
            paciente=request.user,
            data_aberta=data_aberta
        )

        horario_agendado.save()

        # TODO: Sugestão Tornar atomico

        data_aberta.agendado = True
        data_aberta.save()

        messages.add_message(request, constants.SUCCESS, 'Horário agendado com sucesso.')

        return redirect('/pacientes/minhas_consultas/')
    
@login_required
def minhas_consultas(request):
    #Realizar os filtros
    if request.method == "GET":
        especialidades = Especialidades.objects.all()
        minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
        return render(request, 'minhas_consultas.html', {'especialidades': especialidades, 'minhas_consultas': minhas_consultas, 'is_medico': is_medico(request.user)})
    
    if request.method == "POST":
        
        data_filtrada = request.POST.get('data_filtrada')
        especialidades = request.POST.get('especialidades')

        if not data_filtrada and not especialidades:
            #messages.add_message(request, constants.WARNING, 'Você precisa fornecer uma data para filtro.')
            especialidades = Especialidades.objects.all()
            minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
            return render(request, 'minhas_consultas.html', {'especialidades': especialidades, 'minhas_consultas': minhas_consultas, 'is_medico': is_medico(request.user)})

        if data_filtrada and not especialidades:
            especialidades = Especialidades.objects.all()
            data_filtrada = datetime.strptime(data_filtrada, '%Y-%m-%d')
            minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=data_filtrada).filter(data_aberta__data__lt=data_filtrada + timedelta(days=1))
            #consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user)
            return render(request, 'minhas_consultas.html', {'minhas_consultas': minhas_consultas, 'is_medico': is_medico(request.user)})
        
        if especialidades and not data_filtrada:
            hoje = datetime.now().date()
            minhas_consultas = Consulta.objects.filter(paciente=request.user, data_aberta__user__dadosmedico__especialidade=especialidades)
            return render(request, 'minhas_consultas.html', {'minhas_consultas': minhas_consultas, 'is_medico': is_medico(request.user)})
            
            

        #data_filtrada = datetime.strptime(data_filtrada, '%Y-%m-%d')
        #consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=data_filtrada).filter(data_aberta__data__lt=data_filtrada + timedelta(days=1))
        #consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user)
        #return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'is_medico': is_medico(request.user)})
    
    

@login_required
def consulta(request, id_consulta):
    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta = id_consulta)
        dado_medico = DadosMedico.objects.get(user=consulta.data_aberta.user)
        return render(request, 'consulta.html', {'documentos': documentos, 'consulta': consulta, 'dado_medico': dado_medico, 'is_medico': is_medico(request.user)})
