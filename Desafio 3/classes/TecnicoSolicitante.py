class TecnicoSolicitante:
    # Propriedades
    idTecnico: int
    matricula: str
    cargo: str
    setor: str

    # Verificar se nome está preenchido
    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        if not valor or not valor.strip(): 
            raise ValueError("Preenchimento do nome deve ser obrigatório!")
        else: 
            self._nome = valor

    # Verificação de valor válido para Papel, segundo as regras de negócio
    @property
    def papel(self):
        return self._papel

    @papel.setter
    def papel(self, valor: str):
        papeis = ["METROLOGISTA", "SIGNATARIO", "SOLICITANTE"]

        if not valor or not valor.strip(): 
            raise ValueError(f"Defina um papel válido: {papeis}")

        valorFormat = valor.upper()
        
        if valorFormat not in papeis: 
            raise ValueError(f"Papel inválido! Deve ser um dos valores: {papeis}")

        self._papel = valorFormat

    # Verificação para turno
    @property
    def turno(self):
        return self._turno

    @turno.setter
    def turno(self, valor: str):
        turnos = ["MATUTINO", "VESPERTINO", "NOTURNO"]
    
        if not valor or not valor.strip():
            self._turno = None
            return
        
        turnoFormat = valor.upper()

        if turnoFormat not in turnos:
            raise ValueError(f"Defina um turno válido: {turnos}")

        self._turno = turnoFormat

    # Verificação de valor para ativo (deve ser 0 ou 1)
    @property
    def ativo(self):
        return self._ativo

    @ativo.setter
    def ativo(self, valor):
        if valor != 0 and valor != 1:
            raise ValueError("Digite um valor válido! Se ativo, digite 1, e se inativo, digite 0")
        self._ativo = valor

    # Verifica se a string foi preenchida. Caso esteja vazia ou nula, retorna None
    def verificaNulos(self, valor):
        if not valor or not valor.strip(): 
            return None
        else: 
            return valor

    # Construtor
    def __init__(self, matricula: str, nome: str, cargo: str, papel: str, setor: str, turno: str, ativo: int = 1, idTecnico: int = None):
        self.matricula = self.verificaNulos(matricula)
        self.cargo = self.verificaNulos(cargo)
        self.setor = self.verificaNulos(setor)
        self.idTecnico = idTecnico

        self.nome = nome
        self.papel = papel
        self.turno = turno
        self.ativo = ativo

    def exibirDadosTecnico(self):
        status = "Ativo" if self.ativo else "Inativo"
        return f"Nome: {self.nome}; Papel: {self.papel}; Cargo: {self.cargo}; Turno: {self.turno}; Status: {status}"

    def exibirStatus(self):
        if self.ativo: 
            return "ATIVO"
        else: 
            return "INATIVO"