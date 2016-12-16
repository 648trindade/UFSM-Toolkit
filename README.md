# UFSM ToolKit
---

**Autor:** Rafael Gauna Trindade

**Versao:** 1.0.0a

**Host**: http://ufsm-toolkit.herokuapp.com/

Este servico representa a implementacao de um servidor Django que realiza 
operacoes comuns para estudantes e servidores da Universidade Federal de Santa 
Maria (UFSM). Dentre os recursos disponiveis estao: Consultas ao portal do 
aluno, consultas a biblioteca, consultas sobre informacoes do Restaurante
Universitario, entre outros.

Essa pagina tem como funcao descrever as funcionalidades disponiveis e como
usa-las corretamente.

# Operacoes disponiveis
---
## /index

Retorna um compilado de informacoes livres. Se uma matricula e uma senha forem 
fornecidos via POST, retorna compilado de informacoes pessoais tambem.

**Parametros POST:**

  * **matricula**: (opcional) matricula do usuario
  * **senha**: (opcional) senha do usuario

## /sequencial

Mesma funcionalidade da index, entretanto realizando operacoes sequencialmente.
Sua existencia deve-se a testes de desempenho internos.

**Parametros POST:**

  * **matricula**: (opcional) matricula do usuario
  * **senha**: (opcional) senha do usuario

## /cardapio

Retorna o cardapio da semana. Se especificado via GET, retorna o cardapio de um 
um especifico.

**Parametros GET:**

  * **ru**: (opcional) Restaurante a ser pesquisado. Opcoes:
    * *ru-campus* - Campus
    * *refeitorio-2* - Campus 2
    * *ru-centro* - Centro

## /notas

Retorna relacao de notas em disciplinas onde se esta atualmente matriculado. Se 
acessado diretamente via POST, uma matricula e senha devem ser fornecidos. 
Especificar ano e periodo e opcional.

**Parametros POST:**

  * **matricula**: matricula do usuario
  * **senha**: senha do usuario
  * **ano**: (opcional) ano da turma
  * **periodo** (opcional) periodo da turma. Opcoes:
    * *100*: Anual
    * *101*: 1. Semestre
    * *102*: 2. Semestre
    * *103*: Curso de Verao
    * *104*: Curso de Inverno
    * *200*: Semestral
    * *300*: Trimestral
    * *301*: 1. Trimestre
    * *302*: 2. Trimestre
    * *303*: 3. Trimestre
    * *304*: 4. Trimestre
    * *400*: Etapas
    * *401*: Etapa 1
    * *402*: Etapa 2
    * *403*: Etapa 3
    * *404*: Etapa 4
    * *500*: NAO UTILIZADOS

## /horario

Retorna relacao de horarios em disciplinas onde se esta atualmente matriculado. 
Se acessado diretamente via POST, uma matricula e senha devem ser fornecidos. 
Especificar ano e periodo e opcional.

**Parametros POST:**

  * **matricula**: matricula do usuario
  * **senha**: senha do usuario
  * **ano**: (opcional) ano da turma
  * **periodo** (opcional) periodo da turma. Opcoes:
    * *100*: Anual
    * *101*: 1. Semestre
    * *102*: 2. Semestre
    * *103*: Curso de Verao
    * *104*: Curso de Inverno
    * *200*: Semestral
    * *300*: Trimestral
    * *301*: 1. Trimestre
    * *302*: 2. Trimestre
    * *303*: 3. Trimestre
    * *304*: 4. Trimestre
    * *400*: Etapas
    * *401*: Etapa 1
    * *402*: Etapa 2
    * *403*: Etapa 3
    * *404*: Etapa 4
    * *500*: NAO UTILIZADOS

## /turmas

Retorna lista de turmas onde se esta atualmente matriculado. Se acessado 
diretamente via POST, uma matricula e senha devem ser fornecidos. Especificar 
ano e periodo e opcional.

**Parametros POST:**

  * **matricula**: matricula do usuario
  * **senha**: senha do usuario
  * **ano**: (opcional) ano da turma
  * **periodo** (opcional) periodo da turma. Opcoes:
    * *100*: Anual
    * *101*: 1. Semestre
    * *102*: 2. Semestre
    * *103*: Curso de Verao
    * *104*: Curso de Inverno
    * *200*: Semestral
    * *300*: Trimestral
    * *301*: 1. Trimestre
    * *302*: 2. Trimestre
    * *303*: 3. Trimestre
    * *304*: 4. Trimestre
    * *400*: Etapas
    * *401*: Etapa 1
    * *402*: Etapa 2
    * *403*: Etapa 3
    * *404*: Etapa 4
    * *500*: NAO UTILIZADOS

## /turma

Retorna informacoes da turma especificada. Se acessado diretamente via POST,
uma matricula, senha e ID da turma devem ser fornecidos.

**Parametros POST:**

  * **matricula**: matricula do usuario
  * **senha**: senha do usuario
  * **id_turma**: ID da turma (consultar portal do aluno)

## /matriz_curricular

Retorna a matriz curricular do curso atual. Se acessado diretamente via GET, 
uma matricula e senha devem ser fornecidos. Especificar ano e periodo e 
opcional.

**Parametros POST:**

  * **matricula**: matricula do usuario
  * **senha**: senha do usuario

## /ultimas_aquisicoes

Retorna ultimas aquisicoes da biblioteca. **(OBS.: atualmente nao-funcional)**

## /historico_emprestimo

Retorna historico de emprestimo. Se acessado diretamente via POST, uma
matricula e senha devem ser fornecidos. **(OBS.: atualmente nao-funcional)**

**Parametros POST:**

  * **matricula**: matricula do usuario
  * **senha**: senha do usuario

## /consulta_agendamento

Retorna historico de agendamentos recentes. Se acessado diretamente via POST, 
uma matricula e senha devem ser fornecidos.  **(OBS.: atualmente nao-funcional)**

**Parametros POST:**

  * **matricula**: matricula do usuario
  * **senha**: senha do usuario

## /calendario

Retorna o calendario academico do ano corrente.

## /agenda_refeicoes

Agenda refeicoes conforme especificado. Parametros POST obrigatorios: matricula 
senha, restaurante, refeicoes, inicio, fim. Retorna resultado da operacao.

**Parametros POST:**

  * **matricula**: matricula do usuario
  * **senha**: senha do usuario
  * **restaurante**: restaurante a agendar refeicoes. Opcoes:
    * *1*: RU - Campus
    * *2*: RU - Centro
    * *3*: RU - Palmeira das Missoes
    * *41*: RU - Refeitorio 2
    * *42*: RU - Cachoeira
    * *4*: RU - Cesnors FW
  * **refeicoes**: lista de tipos refeicoes a agendar. Opcoes:
    * *1*: Cafe
    * *2*: Almoco
    * *3*: Jantar
    * *4*: Distribuicao
  * **inicio**: data de inicio, no formato dd/mm/aaaa
  * **fim**: data de termino, no formato dd/mm/aaaa
