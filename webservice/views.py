from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup as bs
import requests
from classes import CardapioDia, Refeicao, RefeicaoItem
import json

# Create your views here.

def index(request):
	dic = {}
	dic['cardapio'] = cardapio(None) 
	return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))

def cardapio(request):
	if request is not None and request.method == 'GET':
		rus = request.GET.get('ru')
		if rus is None:
			rus = ['ru-campus','refeitorio-2','ru-centro']
	elif request is None:
		rus = ['ru-campus','refeitorio-2','ru-centro']
	else:
		return HttpResponse('')
	
	dic = {}
	for ru in rus:
		html = requests.get("http://ru.ufsm.br/cardapio/" + ru).content
		soup = bs(html, 'html.parser',from_encoding="utf-8")

		cardapios = []
		for a in soup.find_all('a', role="tab"):
			c = CardapioDia()
			c.dia = a.get("aria-controls")
			c.local = "ru-campus"
			cardapios.append(c)
		
		i=0
		for div in soup.find_all('div', class_="panel panel-primary"):
			c = cardapios[i//2]
			c.refeicoes.append(Refeicao())
			for td in div.find_all('td'):
				if len(td.find_all('a')) is 0:
					c.refeicoes[-1].calorias = td.get_text()
				else:
					img = td.find('img')['src']
					tipo = int(img[img.rfind('/') + 1 : img.rfind('.')])
					a = td.find('a')
					titulo = a['data-titulo']
					ingredientes = a['data-ingredientes']
					r = RefeicaoItem()
					r.toIngredientes(ingredientes)
					r.tipo = tipo
					r.titulo = titulo
					c.refeicoes[-1].itens.append(r)
			i+=1
	
		dic[ru] = [c.toDic() for c in cardapios]
	
	if request is not None:
		return HttpResponse(json.dumps(dic, indent=4, sort_keys=True))
	else:
		return dic
