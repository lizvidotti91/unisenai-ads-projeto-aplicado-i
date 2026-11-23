import re
from database import ConexaoBanco, EquipamentoDAO
from entidade import Equipamento

# Responsável pela sanitizacao dos dados de entrada
# Gerenciar o cadastro sem duplicidade de equipamentos, tanto da máquina MMC quanto do instrumento que está sendo calibrado
class EquipamentoService:
    # Método de inicializacao
    def __init__(self, conexao: ConexaoBanco):
        self.conexao = conexao # Conexao com o banco de dados
        self.dao = EquipamentoDAO(conexao) # Instancia o objeto EquipamentoDAO

    # Aplicacao das regras de limpeza definidas no Desafio 1
    @staticmethod
    def limpar_texto(valor, padrao: str = None) -> str | None:
        if valor is None:
            return padrao
        texto = re.sub(r"[\x00-\x1f\x7f]", "", str(valor)) # remocao de caracteres invisiveis e quebras de linha
        texto = re.sub(r"\s+", " ", texto).strip() # reduz espacos duplicados
        if not texto or texto.lower() in {"-", "----", "n/a", "null", "none", "nao consta", "não consta"}:
            return padrao # trata valores vazios como o padrão passado por parametro "NAO INFORMADO"
        return texto

    # Metodo que verifica se já existe um equipamento cadastrado no banco
    # Caso não exista, cria um equipamento novo
    def salvar(
        self, tag: str, tipo: str, numero_serie: str, nome: str,
        fabricante: str = None, solicitante_id: int = None
    ) -> int:
        tag_limpa = self.limpar_texto(tag)
        if not tag_limpa:
            raise ValueError("Código/TAG do equipamento é obrigatório.") # Verifica se o campo foi preenchido

        row = self.conexao.consultar_um(
            "SELECT idEquipamento FROM equipamentos WHERE tagEquipamento = ?",
            (tag_limpa,) # consulta no banco se já existe um equipamento com a TAG informada
        )
        if row:
            return row["idEquipamento"] # se existe um equipamento, retorna o id do equipamento

        # Cria um novo equipamento quando a consulta não retorna o id do equipamento
        novo = Equipamento(
            tagEquipamento=tag_limpa,
            tipo=tipo,
            numeroSerie=self.limpar_texto(numero_serie) or f"SN-{tag_limpa}",
            nomeEquipamento=self.limpar_texto(nome, padrao="Dispositivo de Controle"),
            fabricante=self.limpar_texto(fabricante, padrao="NAO INFORMADO"),
            solicitanteId=solicitante_id
        )
        return self.dao.inserir(novo)