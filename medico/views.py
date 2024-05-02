from datetime import datetime, timedelta
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from medico.models import DadosMedico, Especialidades, DatasAbertas, is_medico
from django.contrib.messages import constants
from django.contrib import messages
from paciente.models import Consulta, Documento, Observacoes
from django.db.models import Count
from django.views.decorators.http import require_GET, require_POST


# Create your views here.


@staff_member_required(login_url='/usuarios/login')
@login_required
def cadastro_medico(request):
    if is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Você já está cadastrado como médico.')
        return redirect('/medicos/abrir_horario')
    
    #if not is_medico(request.user):
    #    messages.add_message(request, constants.WARNING, 'você não tem acesso a essa página.')
    #    return redirect('/usuarios/sair')

    if request.method == "GET":
        especialidades = Especialidades.objects.all()
        return render(request, 'cadastro_medico.html', {'especialidades': especialidades})
    elif request.method == "POST":
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')

        #TODO: Validar todos os campos

        dados_medico = DadosMedico(
            crm=crm,
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            rg=rg,
            cedula_identidade_medica=cim,
            foto=foto,
            user=request.user,
            descricao=descricao,
            especialidade_id=especialidade,
            valor_consulta=valor_consulta
        )
        dados_medico.save()

        messages.add_message(request, constants.SUCCESS, 'Cadastro médico realizado com sucesso.')

        return redirect('/medicos/abrir_horario')
    

@login_required
def abrir_horario(request):

    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    if request.method == "GET":
        datas_abertas = DatasAbertas.objects.filter(user=request.user)
        dados_medicos = DadosMedico.objects.get(user=request.user)
        return render(request, 'abrir_horario.html', {'dados_medicos': dados_medicos, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})
        
    elif request.method == "POST":
        data = request.POST.get('data')
        data_formatada = datetime.strptime(data, "%Y-%m-%dT%H:%M")
       
        if data_formatada <= datetime.now():
            messages.add_message(request, constants.WARNING, 'A data deve ser maior ou igual a data atual.')
            return redirect('/medicos/abrir_horario')

        horario_abrir = DatasAbertas(
            data=data,
            user=request.user
        )

        horario_abrir.save()
        messages.add_message(request, constants.SUCCESS, 'Horário cadastrado com sucesso.')
        return redirect('/medicos/abrir_horario')


@require_POST
@login_required
def consultas_medico(request):

    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    if request.method == "POST":
        data_filtrada = request.POST.get('data_filtrada')
        if not data_filtrada :
            #messages.add_message(request, constants.WARNING, 'Você precisa fornecer uma data para filtro.')
            hoje = datetime.now().date()
            consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1))
            consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user)
            return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'consultas_restantes': consultas_restantes, 'is_medico': is_medico(request.user)})

        data_filtrada = datetime.strptime(data_filtrada, '%Y-%m-%d')
        consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=data_filtrada).filter(data_aberta__data__lt=data_filtrada + timedelta(days=1))
        consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user)
        return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'is_medico': is_medico(request.user)})

    hoje = datetime.now().date()
    consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1))
    consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user)

    return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'consultas_restantes': consultas_restantes, 'is_medico': is_medico(request.user)})


@login_required
def consulta_area_medico(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    

    if request.method == "GET":
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta=consulta)
        observacoes = Observacoes.objects.filter(consulta=consulta)
        return render(request, 'consulta_area_medico.html', {'observacoes':observacoes,'documentos': documentos, 'consulta': consulta,'is_medico': is_medico(request.user)}) 
    
    elif request.method == "POST":
        # Inicializa a consulta + link da chamada
        consulta = Consulta.objects.get(id=id_consulta)
        link = request.POST.get('link')

        if consulta.status == 'C':
            messages.add_message(request, constants.WARNING, 'Essa consulta já foi cancelada, você não pode inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        elif consulta.status == "F":
            messages.add_message(request, constants.WARNING, 'Essa consulta já foi finalizada, você não pode inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        
        consulta.link = link
        consulta.status = 'I'
        consulta.save()

        messages.add_message(request, constants.SUCCESS, 'Consulta inicializada com sucesso.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    

@login_required
def finalizar_consulta(request, id_consulta):
    status_pagto = request.GET.get('pagto')
    print("Paga:", status_pagto)
   
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)
    
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!.')
        return redirect(f'/medicos/abrir_horario/')
    
    if not status_pagto:
        messages.add_message(request, constants.ERROR, 'É preciso informar se houve ou não o pagamento da consulta antes de finalizar.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    if status_pagto == 'S':
        consulta.status_pagto == 'S'
    else:     
        messages.add_message(request, constants.WARNING, 'Esta consulta não foi paga ainda')
        consulta.status_pagto == 'N'


    consulta.status = 'F'
    consulta.save()
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    

@login_required
def cancelar_consulta(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    
    consulta = Consulta.objects.get(id=id_consulta)
    
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!.')
        return redirect(f'/medicos/abrir_horario/')

    consulta.status = 'C'
    consulta.save()
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')


@login_required
def add_documento(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)
    
    if consulta.data_aberta.user != request.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    
    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')

    if not documento:
        messages.add_message(request, constants.WARNING, 'Adicione o documento.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

    documento = Documento(
        consulta=consulta,
        titulo=titulo,
        documento=documento

    )

    documento.save()

    messages.add_message(request, constants.SUCCESS, 'Documento enviado com sucesso!')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')


@login_required
def del_documento(request, id_consulta, id_documento):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)
    
    if consulta.data_aberta.user != request.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!')
        return redirect(f'/medicos/consultas_medico')
    
    documento = Documento.objects.get(id=id_documento)

    #print(documento.titulo)
    #print(documento.id)

    documento.delete()

    messages.add_message(request, constants.SUCCESS, 'Documento removido com sucesso!')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')


def salvar_observacao(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)
    
    if consulta.data_aberta.user != request.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    
    observacao = request.POST.get('descricao')
    

    observacao = Observacoes(
            observacao=observacao,
            consulta=consulta

        )

    observacao.save()

    messages.add_message(request, constants.SUCCESS, 'Observação enviada com sucesso!')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')


def grafico_desempenho_medico(request):

    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'você não tem acesso a essa página.')
        return redirect('/usuarios/sair')
    
    consultas = Consulta.objects.filter(data_aberta__user=request.user)\
    .filter(data_aberta__data__range = [datetime.now().date() - timedelta(days=7), datetime.now().date() + timedelta(days=1) ])\
    .values('data_aberta__data').annotate(quantidade=Count('id'))

    datas = [i['data_aberta__data'].strftime("%d-%m-%Y") for i in consultas]
    quantidade = [i['quantidade'] for i in consultas]

    #print(datas)
    #print(quantidade)

    return render(request, 'dashboard.html', {'datas':datas, 'quantidade':quantidade, 'is_medico': is_medico(request.user)})

