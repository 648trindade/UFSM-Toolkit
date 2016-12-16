"""ufsmtoolkit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import webservice.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', webservice.views.index),
    url(r'^cardapio$', webservice.views.cardapio),
    url(r'^sequencial$', webservice.views.sequencial),
    url(r'^turmas$', webservice.views.turmas),
    url(r'^turma$', webservice.views.turma),
    url(r'^sobre$', webservice.views.sobre),
    url(r'^ultimas_aquisicoes$', webservice.views.ultimas_aquisicoes),
    url(r'^historico_emprestimo$', webservice.views.historico_emprestimo),
    url(r'^calendario$', webservice.views.calendario),
    url(r'^consulta_agendamento$', webservice.views.consulta_agendamento),
    url(r'^agenda_refeicoes$', webservice.views.agenda_refeicoes),
    url(r'^notas$', webservice.views.notas),
    url(r'^horario$', webservice.views.horario),
    url(r'^matriz_curricular$', webservice.views.matriz_curricular),
    url(r'^template$', webservice.views.template)
]
