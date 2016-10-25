class CardapioDia:
    def __init__(self):
        self.dia = ""
        self.refeicoes = list()
        self.local = ""
    
    def toDic(self):
        dic = self.__dict__
        dic['refeicoes'] = [refeicao.toDic() for refeicao in self.refeicoes]
        return dic

class Refeicao:
    def __init__(self):
        self.tipo = ""
        self.itens = list()
        self.calorias = 0.0
    
    def toDic(self):
        dic = self.__dict__
        dic['itens'] = [item.toDic() for item in self.itens]
        return dic

class RefeicaoItem:
    def __init__(self):
        self.tipo = 0
        self.titulo = ""
        self.ingredientes = list()
        self.calorias = 0.0
    
    def toIngredientes(self, string):
        if len(string) is 0:
            return
        elif string[-1] == '|':
            string = string[:-1]
        for s in string.split("|"):
            ing, calorias = s.split('=')
            self.ingredientes.append({'ingrediente':ing, 'calorias':float(calorias)})
    
    def toDic(self):
        return self.__dict__