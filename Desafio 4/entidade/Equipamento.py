class Equipamento:
    # Propriedades
    idEquipamento: int
    modelo: str
    faixaMedicao: str
    drawningNo: str
    partNo: str
    rastreabilidade: str

    def verificaNulos(self, valor):
        if not valor or not valor.strip(): 
            return None
        else: 
            return valor

    def verificaCampoObrigatorio(self, valor, campo):
        if not valor or not valor.strip():
            raise ValueError(f"Campo obrigatório. Informe um valor válido para {campo}")
        return valor.strip()

    @property
    def tagEquipamento(self):
        return self._tagEquipamento

    @tagEquipamento.setter
    def tagEquipamento(self, valor):
        self._tagEquipamento = self.verificaCampoObrigatorio(valor, "Tag do Equipamento")

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        tipos = ['MMC', 'INSTRUMENTO']
        valor_validado = self.verificaCampoObrigatorio(valor, "Tipo")
        tipoFormat = valor_validado.upper()
        
        if tipoFormat not in tipos: 
            raise ValueError(f"Informe valor válido para tipo: {tipos}")
        self._tipo = tipoFormat

    @property
    def numeroSerie(self):
        return self._numeroSerie

    @numeroSerie.setter
    def numeroSerie(self, valor):
        self._numeroSerie = self.verificaCampoObrigatorio(valor, "Número de Série")

    @property
    def nomeEquipamento(self):
        return self._nomeEquipamento

    @nomeEquipamento.setter
    def nomeEquipamento(self, valor):
        self._nomeEquipamento = self.verificaCampoObrigatorio(valor, "Nome do Equipamento")

    @property
    def fabricante(self):
        return self._fabricante

    @fabricante.setter
    def fabricante(self, valor):
        if not valor or not valor.strip():
            self._fabricante = "NAO INFORMADO"
        else:
            self._fabricante = valor.strip()

    # Validação de Solicitante Id
    @property
    def solicitanteId(self):
        return self._solicitanteId

    @solicitanteId.setter
    def solicitanteId(self, valor):
        if valor is None:
            self._solicitanteId = None; # o Banco aceita valores nulos
            return;

        try: 
            self._solicitanteId = int(valor) # Verifica se o Id informado é um número inteiro
        except(ValueError, TypeError):
            raise ValueError(f"Id do Solicitante inválido: {valor}")

    # Construtor
    def __init__(self, tagEquipamento: str, tipo: str, numeroSerie: str, nomeEquipamento: str, fabricante: str = None, modelo: str = None, faixaMedicao: str = None, drawningNo: str = None, partNo: str = None, rastreabilidade: str = None, solicitanteId: int = None, idEquipamento: int = None):
        self.idEquipamento = idEquipamento
        
        # Atribuindo opcionais
        self.modelo = self.verificaNulos(modelo)
        self.faixaMedicao = self.verificaNulos(faixaMedicao)
        self.drawningNo = self.verificaNulos(drawningNo)
        self.partNo = self.verificaNulos(partNo)
        self.rastreabilidade = self.verificaNulos(rastreabilidade)

        # Atribuindo obrigatórios (passam pelos setters)
        self.tagEquipamento = tagEquipamento
        self.tipo = tipo
        self.numeroSerie = numeroSerie
        self.nomeEquipamento = nomeEquipamento
        self.fabricante = fabricante
        self.solicitanteId = solicitanteId

    def exibirDadosEquipamento(self):
        dono = f"Solicitante ID: {self.solicitanteId}" if self.solicitanteId else "Equipamento Interno (Schulz)"
        return (f"Equipamento [ID: {self.idEquipamento}] | Tag: {self.tagEquipamento} | "
                f"Nome: {self.nomeEquipamento} | Tipo: {self.tipo} | Série: {self.numeroSerie} | "
                f"Fabricante: {self.fabricante} | {dono}")