class CardapioDia:
    def __init__(self):
        self.dia = ""
        self.refeicoes = list()
        self.local = ""

    def to_dic(self):
        dic = self.__dict__
        dic['refeicoes'] = [refeicao.to_dic() for refeicao in self.refeicoes]
        return dic

class Refeicao:
    def __init__(self):
        self.tipo = ""
        self.itens = list()
        self.calorias = 0.0

    def to_dic(self):
        dic = self.__dict__
        dic['itens'] = [item.to_dic() for item in self.itens]
        return dic

class RefeicaoItem:
    def __init__(self):
        self.tipo = 0
        self.titulo = ""
        self.ingredientes = list()
        self.calorias = 0.0

    def to_ingredientes(self, string):
        if len(string) is 0:
            return
        elif string[-1] == '|':
            string = string[:-1]
        for raw in string.split("|"):
            ing, calorias = raw.split('=')
            self.ingredientes.append({'ingrediente':ing, 'calorias':float(calorias)})

    def to_dic(self):
        return self.__dict__

class Turma:
    def __init__(self, soup):
        rows = soup.find_all('div', class_='row')
        tables = soup.find_all('table')

        spans = rows[0].find_all('div')
        self.name = spans[0].find('a').get_text()
        self.codigo_turma = spans[1].find_all('span')[1].get_text()
        self.codigo_disc = spans[2].find_all('span')[1].get_text()
        self.matricula = spans[3].find_all('span')[1].get_text()

        spans = rows[1].find_all('div')
        self.curso = spans[0].find('a').get_text()
        self.professores = [li.get_text() for li in spans[1].find_all('li')]

        spans = rows[2].find_all('div')
        self.carga = spans[0].find_all('span')[1].get_text()
        self.minimo = spans[1].find_all('span', recursive=False)[2].get_text()
        self.presencas = spans[2].get_text().strip().split(' ')[-1]
        self.faltas = spans[3].find_all('span')[1].get_text()

        # horarios
        rows = tables[0].find('tbody').find_all('tr')
        columns = ('dia_semana', 'inicio', 'fim', 'qtd', 'tipo')
        self.horarios = []
        for row in rows:
            i, horario = 0, {}
            for data in row.find_all('td'):
                horario[columns[i]] = data.get_text()
                i += 1
            self.horarios.append(horario)

        # aulas
        self.aulas = []
        if len(tables) > 1:
            rows = tables[1].find('tbody').find_all('tr')
            columns = ('dia', 'qtd', 'tipo')
            for row in rows:
                i, aula = 0, {}
                for data in row.find_all('td')[:-2]:
                    aula[columns[i]] = data.get_text()
                    i += 1
                aula['resumo'] = row.find_all('td')[-2].find_all('span')[1].get_text()
                aula['presencas'] = [
                    i["class"] == "icon-ok presente" for i in row.find_all('td')[-1].find_all('i')
                ]
                self.aulas.append(aula)

        # notas
        self.notas = []
        if len(tables) > 2:
            rows = tables[2].find('tbody').find_all('tr')
            columns = ('avaliacao', 'peso', 'nota')
            for row in rows:
                i, nota = 0, {}
                for data in row.find_all('td'):
                    nota[columns[i]] = data.get_text()
                    i += 1
                self.notas.append(nota)

    def to_dic(self):
        return self.__dict__
