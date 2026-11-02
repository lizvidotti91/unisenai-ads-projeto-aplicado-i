from datetime import datetime

class Medicao:
    # Propriedades
    idMedicao: int
    equipamentoId: int
    padraoId: int
    tecnicoId: int
    numeroCertificacao: str
    dtHoramedicao: str
    planoMedicao: str
    codigo: str
    parametro: str
    eixoReferencia: str
    unidade: str
    valorNominal: float
    toleranciaSuperior: float
    toleranciaInferior: float
    medida1: float
    medida2: float
    valorObtido: float
    desvio: float

    # Verifica campos opcionais, e preenche com valor Nulo ou válido
    def verificaNulos(self, valor):
        if not valor or (isinstance(valor, str) and not valor.strip()): 
            return None
        return valor

    # Verifica campos obrigatórios, exibindo mensagem de erro para o campo vazio
    def verificaCampoObrigatorio(self, valor, campo):
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ValueError(f"Campo obrigatório. Informe um valor válido para {campo}")
        return valor

    # Verificar Unidade
    @property
    def unidade(self):
        return self._unidade

    @unidade.setter
    def unidade(self, valor):
        unidades = ['mm', 'um', 'graus'] # Define as unidades válidas no banco
        valValidado = self.verificaCampoObrigatorio(valor, "Unidade")
        valFormat = str(valValidado).strip().lower() # Converte para letras minúsculas
        
        if valFormat not in unidades:
            raise ValueError(f"Unidade inválida! Deve ser uma de: {unidades}") # Verifica se o valor digitado está nas unidades válidas
        self._unidade = valFormat

    # Valida se Status foi preenchido corretamente
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, valor):
        statuses = ['APROVADO', 'REPROVADO', 'PENDENTE'] # Define os status válidos no banco
        if not valor:
            self._status = 'PENDENTE' # Se não for informado nenhum valor, preencher com o valor padrão
            return
        
        statusFormat = str(valor).strip().upper() # Converte o status informado para maiúsculas
        if statusFormat not in statuses:
            raise ValueError(f"Status inválido! Deve ser um de: {statuses}") # Verifica se o valor informado é um status válido
        self._status = statusFormat

    # Construtor
    def __init__(self, equipamentoId: int, tecnicoId: int, codigo: str, parametro: str, valorNominal: float, medida1: float, valorObtido: float, padraoId: int = None, numeroCertificacao: str = None, planoMedicao: str = None, eixoReferencia: str = None, unidade: str = 'mm', toleranciaSuperior: float = None, toleranciaInferior: float = None, medida2: float = None, status: str = 'PENDENTE', idMedicao: int = None, dtHoraMedicao: str = None):
        self.idMedicao = idMedicao
        self.equipamentoId = equipamentoId
        self.tecnicoId = tecnicoId
        self.codigo = codigo
        self.parametro = parametro
        self.valorNominal = float(valorNominal) # Salva o tipo de dado como Float
        self.medida1 = float(medida1) # Salva o tipo de dado como Float
        self.valorObtido = float(valorObtido) # Salva o tipo de dado como Float

        # Para verificação dos campo opcionais, usar o método verifica nulos
        self.padraoId = padraoId
        self.numeroCertificacao = self.verificaNulos(numeroCertificacao)
        self.planoMedicao = self.verificaNulos(planoMedicao)
        self.eixoReferencia = self.verificaNulos(eixoReferencia)

        # Verifica se os valores de tolerância e medida2 estão preenchidos corretamente e converte para Float
        # Como os campos são opcionais, preenchemos com None ou o valor corretamente com o tipo de dado Float
        if toleranciaSuperior is None: self.toleranciaSuperior = None
        else: self.toleranciaSuperior = float(toleranciaSuperior)

        if toleranciaInferior is None: self.toleranciaInferior = None
        else: self.toleranciaInferior = float(toleranciaInferior)

        if medida2 is None: self.medida2 = None
        else: self.medida2 = float(medida2)

        # Verificar os valores de unidade e status através dos setters
        self.unidade = unidade
        self.status = status

        # Tratamento da Data/Hora da Medição (ISO 8601)
        if not dtHoraMedicao:
            self.dtHoramedicao = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Se o valor não vem preenchido, converter a data/hora atual do sistema para String
        else:
            self.dtHoramedicao = dtHoraMedicao

        # Cálculo automático do desvio (valor_obtido - valor_nominal)
        self.desvio = self.valorObtido - self.valorNominal

    def exibirDadosMedicao(self):
        return (f"Medição [ID: {self.idMedicao}] | Código: {self.codigo} ({self.parametro}) | "
                f"Nominal: {self.valorNominal} | Obtido: {self.valorObtido} | "
                f"Desvio: {self.desvio:.4f} {self.unidade} | Status: {self.status}")