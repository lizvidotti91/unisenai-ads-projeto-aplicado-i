import re
from database import ConexaoBanco, TecnicoDAO
from entidade import TecnicoSolicitante

# Responsavel por validar os nomes, garantir o cadastro único dos Metrologistas, Solicitantes e Signatários da Schulz
class TecnicoService:
    # Inicializacao
    def __init__(self, conexao: ConexaoBanco):
        self.conexao = conexao # conexao do banco de dados
        self.dao = TecnicoDAO(conexao) # instancia o objeto Tecnico DAO

    # Validar e padronizar os nomes informados
    @staticmethod
    def limpar_nome(valor: str) -> str | None:
        if valor is None:
            return None # Verifica nomes nulos
        texto = re.sub(r"[\x00-\x1f\x7f]", "", str(valor)) # remove caracteres invisiveis e quebras de linha
        texto = re.sub(r"\s+", " ", texto).strip() # remove espacos adicionais
        if not texto or texto.lower() in {"-", "----", "n/a", "null", "none"}:
            return None # verifica se o valor informado corresponde a valores nulos
        return texto.title() # retorna nomes informados no padrão correto. Ex.: retorna Elisete Rocha, ao inves de elisete rocha ou ELISETE ROCHA

    # Lista de papeis e turnos válidos
    PAPEIS_VALIDOS = {"METROLOGISTA", "SIGNATARIO", "SOLICITANTE"}
    TURNOS_VALIDOS = {"MATUTINO", "VESPERTINO", "NOTURNO"}

    # Metodo para a insercao do registro no banco de dados
    def salvar(self, nome: str, papel: str, setor: str = None, turno: str = None, matricula: str = None) -> int:
        nome_limpo = self.limpar_nome(nome) # valida o nome informado
        if not nome_limpo:
            raise ValueError(f"Nome obrigatório ausente para o papel '{papel}'.") # retorna erro, pois nome deve ser campo obrigatorio

        if not papel or str(papel).strip().upper() not in self.PAPEIS_VALIDOS:
            # Verifica se o valor informado para o papel é valido e exibe mensagem de erro para valores invalidos
            raise ValueError(f"Papel inválido: '{papel}'. Valores permitidos: {sorted(self.PAPEIS_VALIDOS)}") 
        # remove espacos adicionais e converte o texto para maiusculas
        papel_limpo = str(papel).strip().upper()

        # Valida turno se informado
        turno_limpo = None
        if turno and str(turno).strip(): # verifica se turno foi preenchido
            t = str(turno).strip().upper() # remove especos adicionais e converte para maiusculas
            if t not in self.TURNOS_VALIDOS:
                # Se o valor informado não for um valor valido, retorna uma mensagem de erro
                raise ValueError(f"Turno inválido: '{turno}'. Valores permitidos: {sorted(self.TURNOS_VALIDOS)}")
            turno_limpo = t # atribui o valor a variavel turno limpo

        # Valida setor e matrícula
        setor_limpo = self.limpar_nome(setor) # valida o setor informado e retorna o valor ou None
        if setor is None: # Caso retorne None
            setor_limpo = "NAO INFORMADO" # atribui o valor padrao

        if matricula and str(matricula).strip():
            matricula_limpa = str(matricula).strip()
        else:
            matricula_limpa = None

        # Verifica se existe o nome + papel no banco de dados
        row = self.conexao.consultar_um(
            "SELECT idTecnico FROM tecnicos WHERE UPPER(nome) = UPPER(?) AND papel = ?",
            (nome_limpo, papel_limpo)
        )
        if row:
            return row["idTecnico"] # se a consulta retorna valor, retorna o id do tecnico

        # Caso o nome nao existe no banco, criar uma nova instancia de tecnico
        novo = TecnicoSolicitante(
            matricula=matricula_limpa,
            nome=nome_limpo,
            cargo=papel_limpo.title(),
            papel=papel_limpo,
            setor=setor_limpo,
            turno=turno_limpo,
            ativo=1
        )
        # Insere no banco de dados
        return self.dao.inserir(novo)