""" Rafael Gauna Trindade """
import multiprocessing as mp
from threading import Thread
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup as bs
import requests, json, Queue, markdown
from classes import CardapioDia, Refeicao, RefeicaoItem, Turma
import utils

# Create your views here.

@csrf_exempt
def index(request):
    """
        Retorna um compilado de informacoes livres. Se uma matricula e uma
        senha forem fornecidos via GET, retorna compilado de informacoes
        pessoais tambem.
    """
    fila = mp.Queue()
    funcoes = [cardapio, ultimas_aquisicoes]

    processos = [
        mp.Process(target=funcao, args=(None, fila, )) for funcao in funcoes
    ]

    if request.method == 'GET':
        session = requests.Session()
        resultado = utils.login(request, session)
        if resultado is not None:
            return resultado
        funcoes = [turmas, notas, horario, matriz_curricular, historico_emprestimo, consulta_agendamento]
        processos += [
            mp.Process(target=funcao, args=(None, session, fila, )) for funcao in funcoes
        ]

    for processo in processos:
        processo.start()
    for processo in processos:
        processo.join()

    dic = {}
    while not fila.empty():
        res = fila.get()
        dic[res['processo']] = res['valor']
    return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))

@csrf_exempt
def sequencial(request):
    """
        Mesma funcionalidade da index, entretanto realizando operacoes
        sequencialmente.
    """
    fila = mp.Queue()

    funcoes = [cardapio, ultimas_aquisicoes]
    for funcao in funcoes:
        funcao(None, fila)

    if request.method == 'GET':
        session = requests.Session()
        resultado = utils.login(request, session)
        if resultado is not None:
            return resultado
        funcoes = [turmas, notas, horario, matriz_curricular, historico_emprestimo, consulta_agendamento]
        for funcao in funcoes:
            funcao(None, session, fila)

    dic = {}
    while not fila.empty():
        res = fila.get()
        dic[res['processo']] = res['valor']
    return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))

def cardapio(request, fila=None):
    """
        Retorna o cardapio da semana. Se especificado via GET, retorna o
        cardapio de um um especifico.
    """
    if request is not None and request.method == 'GET':
        rus = request.GET.get('ru')
        if rus is None:
            rus = ['ru-campus', 'refeitorio-2', 'ru-centro']
        else:
            rus = rus.split(",")
    elif request is None:
        rus = ['ru-campus', 'refeitorio-2', 'ru-centro']
    else:
        return HttpResponse('')

    dic = {}
    for ru in rus:
        html = requests.get("http://ru.ufsm.br/cardapio/" + ru).content
        soup = bs(html, 'html.parser', from_encoding="utf-8")

        cardapios = []
        for hyperlink in soup.find_all('a', role="tab"):
            carte = CardapioDia()
            carte.dia = hyperlink.get("aria-controls")
            carte.local = "ru-campus"
            cardapios.append(carte)

        i = 0
        for div in soup.find_all('div', class_="panel panel-primary"):
            carte = cardapios[i//2]
            carte.refeicoes.append(Refeicao())
            for tdata in div.find_all('td'):
                if len(tdata.find_all('a')) is 0:
                    carte.refeicoes[-1].calorias = tdata.get_text()
                else:
                    img = tdata.find('img')['src']
                    tipo = int(img[img.rfind('/') + 1 : img.rfind('.')])
                    hyperlink = tdata.find('a')
                    titulo = hyperlink['data-titulo']
                    ingredientes = hyperlink['data-ingredientes']
                    refeicao = RefeicaoItem()
                    refeicao.to_ingredientes(ingredientes)
                    refeicao.tipo = tipo
                    refeicao.titulo = titulo
                    carte.refeicoes[-1].itens.append(refeicao)
            i += 1

        dic[ru] = [c.to_dic() for c in cardapios]

    if request is not None:
        return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))
    elif fila is not None:
        fila.put({'processo':'cardapio', 'valor':dic})

def turmas(request, session=requests.Session(), fila=None):
    """
        Retorna lista de turmas onde se esta atualmente matriculado. Se acessado
        diretamente via GET, uma matricula e senha devem ser fornecidos.
        Especificar ano e periodo e opcional.
    """
    ano = periodo = None
    if request is not None:
        login = utils.login(request, session)
        if login is not None:
            return login
        ano = request.GET.get('ano')
        periodo = request.GET.get('periodo')
    
    if not (ano and periodo):
        ano, periodo = utils.ano_periodo()
    id_aluno = utils.get_id_aluno(session)
    
    html = session.post(
        "https://portal.ufsm.br/aluno/turmas/list.html",
        data={"ano":ano, "periodo":periodo, "alunoCursos": id_aluno}
    ).content

    soup = bs(html, 'html.parser', from_encoding="utf-8")
    table = soup.find('tbody')
    if table is None:
        print "Tabela nao encontrada: lista de turmas."
        fila.put({'processo':'turmas', 'valor':{}})
        return
    threads = []
    fila_turmas = Queue.Queue()
    for trow in table.find_all('tr'):
        thread = Thread(target=turma, args=(None, session, trow.find('td').find('a')['href'], fila_turmas))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    dic = []
    while not fila_turmas.empty():
        dic.append(fila_turmas.get())

    if request is not None:
        return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))
    elif fila is not None:
        fila.put({'processo':'turmas', 'valor':dic})

def turma(request, session=requests.Session(), url=None, fila=None):
    """
        Retorna informacoes da turma especificada. Se acessado diretamente via
        GET, uma matricula, senha e ID da turma devem ser fornecidos.
    """
    if request is not None:
        login = utils.login(request, session)
        if login is not None:
            return login

    if url is None:
        url = 'https://portal.ufsm.br/aluno/turmas/turma.html?itemCurriculoAluno='
        url += request.GET.get('id_turma')
    else:
        url = 'https://portal.ufsm.br' + url
    html = session.get(url).content
    soup = bs(html, 'html.parser', from_encoding="utf-8")
    dic = Turma(soup).to_dic()

    if request is not None:
        return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))
    fila.put(dic)


def ultimas_aquisicoes(request, fila=None):
    """
        Retorna ultimas aquisicoes da biblioteca.
    """
    url = "https://portal.ufsm.br/biblioteca/relatorio/ultimasAquisicoes.html"
    colunas = ['num', 'cod', 'titulo', 'autor', 'inclusao', 'biblioteca']
    dic = utils.leitura_tabela(url, colunas)

    if request is None:
        fila.put({'processo': 'ultimas_aquisicoes', 'valor': dic})
    else:
        return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))

def historico_emprestimo(request, session=requests.Session(), fila=None):
    """
        Retorna historico de emprestimo. Se acessado diretamente via GET, uma
        matricula e senha devem ser fornecidos.
    """
    if request is not None:
        login = utils.login(request, session)
        if login is not None:
            return login

    url = "https://portal.ufsm.br/biblioteca/leitor/historicoEmprestimos.html"
    colunas = ['cod', 'titulo', 'biblioteca', 'retirada', 'devolucao', 'renovacao', 'situacao']
    dic = utils.leitura_tabela(url, colunas, session)

    if request is None:
        fila.put({'processo': 'historico_emprestimo', 'valor': dic})
    else:
        return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))

def consulta_agendamento(request, session=requests.Session(), fila=None):
    """
        Retorna historico de agendamentos recentes. Se acessado diretamente via
        GET, uma matricula e senha devem ser fornecidos.
    """
    if request is not None:
        login = utils.login(request, session)
        if login is not None:
            return login

    url = "https://portal.ufsm.br/ru/usuario/consultaAgendamento.html"
    colunas = ['id','dia', 'refeicao', 'restaurante', 'realizada', 'limite_cancelamento', 'agendamento']
    dic = utils.leitura_tabela(url, colunas, session)
    for agendamento in dic:
        agendamento.pop("id")

    if request is None:
        fila.put({'processo': 'consulta_agendamento', 'valor': dic})
    else:
        return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))

def calendario(request):
    """
        Retorna o calendario academico.
    """
    cal = open("static/json/calendario.json")
    dic = json.load(cal)
    return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))

def agenda_refeicoes(request):
    """
        Agenda refeicoes conforme especificado. Parametros GET obrigatorios:
        matricula, senha, restaurante, refeicoes, inicio, fim. Retorna
        resultado da operacao.
    """
    session = requests.Session()
    login = utils.login(request, session)
    if login is not None:
        return login

    restaurante = request.GET.get('restaurante')
    refeicoes = request.GET.get('refeicoes')
    inicio = request.GET.get('inicio')
    fim = request.GET.get('fim')

    url = "https://portal.ufsm.br/ru/usuario/agendamento.html"
    html = session.post(url, data={
        'restaurante': restaurante,
        'tiposRefeicao': refeicoes,
        'periodo.inicio': inicio,
        'periodo.fim': fim
    })

    soup = bs(html.content, "html.parser", from_encoding="utf-8")
    linhas = soup.find_all('div', class_="row box narrow no-margin-v stroked-bottom")
    dic = []
    colunas = ['data', 'tipo', 'sucesso', 'observacao']
    for resultado in linhas:
        data = resultado.find_all('div', recursive=False)
        linha = {}
        for i in range(len(data)):
            linha[colunas[i]] = data[i].get_text().strip('\n ')
        dic.append(linha)

    return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))

def sobre(request):
    """
        Retorna ajuda sobre o servico.
    """
    with open('static/markdown/sobre.md') as md:
        html = markdown.markdown(md.read(), output_format="html5", encoding="utf-8")
    return render(request, 'index.html', context={'sobre':html})

def notas(request, session=requests.Session(), fila=None):
    """
        Retorna relacao de notas em disciplinas onde se esta atualmente 
        matriculado. Se acessado diretamente via GET, uma matricula e senha 
        devem ser fornecidos. Especificar ano e periodo e opcional.
    """
    ano = periodo = None
    if request is not None:
        login = utils.login(request, session)
        if login is not None:
            return login
        ano = request.GET.get('ano')
        periodo = request.GET.get('periodo')
    
    if not (ano and periodo):
        ano, periodo = utils.ano_periodo()
    id_aluno = utils.get_id_aluno(session)
    
    html = session.post(
        "https://portal.ufsm.br/aluno/relatorio/quadroNotas/index.html",
        data={"ano":ano, "periodo":periodo, "alunoCursos": id_aluno}
    ).content

    soup = bs(html, 'html.parser', from_encoding="utf-8")
    accordion = soup.find('div', attrs={"class":"accordion"})
    dic = []
    for disciplina in accordion.find_all('div', class_="accordion-group"):
        disc = {'notas':[]}
        disc['nome'] = disciplina.find_all('div', recursive=False)[0].get_text()
        tbody = disciplina.find('tbody')
        if tbody is not None:
            colunas = ['avaliacao', 'faltas', 'nota']
            disc['notas'] = utils.leitura_tabela(None, colunas, None, tbody)
            # for trow in tbody.find_all('tr'):
            #     nota = {}
            #     nota['avaliacao'] = trow.find_all('td')[0].get_text()
            #     nota['faltas'] = trow.find_all('td')[1].get_text()
            #     nota['nota'] = trow.find_all('td')[2].get_text()
            #     disc['notas'].append(nota)
        dic.append(disc)

    if request is not None:
        return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))
    elif fila is not None:
        fila.put({'processo':'notas', 'valor':dic})

def horario (request, session=requests.Session(), fila=None):
    """
        Retorna relacao de horarios em disciplinas onde se esta atualmente 
        matriculado. Se acessado diretamente via GET, uma matricula e senha 
        devem ser fornecidos. Especificar ano e periodo e opcional.
    """
    ano = periodo = None
    if request is not None:
        login = utils.login(request, session)
        if login is not None:
            return login
        ano = request.GET.get('ano')
        periodo = request.GET.get('periodo')
    
    if not (ano and periodo):
        ano, periodo = utils.ano_periodo()
    id_aluno = utils.get_id_aluno(session)
    
    html = session.post(
        "https://portal.ufsm.br/aluno/relatorio/quadroHorariosAluno/form.html",
        data={"ano":ano, "periodo":periodo, "alunoCursos": id_aluno}
    ).content

    soup = bs(html, 'html.parser', from_encoding="utf-8")
    tbody = soup.find('div', id='tab1').find('tbody')
    dic = {}
    if tbody is not None:
        colunas = ['dia', 'horario', 'periodo',	'tipo', 'disciplina', 'codigo', 'turma']
        dic = utils.leitura_tabela(None, colunas, None, tbody)
    
    if request is not None:
        return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))
    elif fila is not None:
        fila.put({'processo':'horario', 'valor':dic})

def matriz_curricular(request, session=requests.Session(), fila=None):
    """
        Retorna a matriz curricular do curso atual. Se acessado diretamente via
        GET, uma matricula e senha devem ser fornecidos. Especificar ano e
        periodo e opcional.
    """
    ano = periodo = None
    if request is not None:
        login = utils.login(request, session)
        if login is not None:
            return login
        ano = request.GET.get('ano')
        periodo = request.GET.get('periodo')
    
    if not (ano and periodo):
        ano, periodo = utils.ano_periodo()
    id_aluno = utils.get_id_aluno(session)
    
    html = session.post(
        "https://portal.ufsm.br/aluno/relatorio/matrizCurricular/index.html",
        data={"ano":ano, "periodo":periodo, "alunoCursos": id_aluno}
    ).content

    soup = bs(html, 'html.parser', from_encoding="utf-8")
    dic = {
        "matriz_curricular": [],
        "dcgs": None,
        "outras_disciplinas": None,
        "integr_curric": None
    }

    matriz = soup.find('div', class_="board large-margin-top bordered rounded shadowed large-margin-bottom")
    for row_div in matriz.find_all(class_='board-row'):
        row = []
        for disc_div in row_div.find(class_='board-row-right').find_all('div',recursive=False):
            text = disc_div.get_text().strip('\n ').split('\n')
            disc = {
                'nome': text[0],
                'codigo': text[1],
                'situacao': text[2]
            }
            row.append(disc)
        dic['matriz_curricular'].append(row)
    
    lista_colunas = [['disciplina', 'codigo', 'situacao'], ['disciplina', 'codigo', 'situacao'], ['descricao', 'CH_vencida', 'CH_exigida', 'percent_vencido']]
    destinos = ['dcgs', 'outras_disciplinas', 'integr_curric']
    tbodys = soup.find_all('tbody')

    for i in range(len(tbodys)):
        dic[destinos[i]] = utils.leitura_tabela(None, lista_colunas[i], None, tbodys[i])
    
    if request is not None:
        return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))
    elif fila is not None:
        fila.put({'processo':'matriz_curricular', 'valor':dic})
