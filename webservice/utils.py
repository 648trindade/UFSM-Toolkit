from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs

def ano_periodo():
    ano = str(datetime.now().year)
    periodo = '10' + str(datetime.now().month/6)
    return ano, periodo

def leitura_tabela(url, keys, session=None, tbody=None):
    if tbody is None:
        if session is None:
            html = requests.get(url).content
        else:
            html = session.get(url).content
        soup = bs(html, 'html.parser', from_encoding="utf-8")
        tbody = soup.find('tbody')
        if tbody is None:
            return {}
    dic = []
    for trow in tbody.find_all('tr'):
        linha = {}
        tdatas = trow.find_all('td')
        for i in range(len(tdatas)):
            linha[keys[i]] = tdatas[i].get_text().strip('\n ')
        dic.append(linha)
    return dic

from django.http import HttpResponse
import requests

def login(request, session):
    if request.method == 'GET':
        matricula = request.GET.get('matricula')
        senha = request.GET.get('senha')
        res = session.post(
            "https://portal.ufsm.br/aluno/j_security_check",
            data={'j_username': matricula, 'j_password': senha}
        )
        if res.url == "https://portal.ufsm.br/aluno/j_security_check":
            return HttpResponse('Login invalido. Matricula: '+str(matricula)+' Senha: '+str(senha))
        return None
    return HttpResponse('')

def get_id_aluno(session):
    page = session.get("https://portal.ufsm.br/aluno/turmas/list.html")
    soup = bs(page.content, 'html.parser', from_encoding="utf-8")
    return soup.find('input', attrs={"name":'alunoCursos'})['value']
