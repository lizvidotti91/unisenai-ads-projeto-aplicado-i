import re
import statistics
import unicodedata
from database import ConexaoBanco, MedicaoDAO
from entidade import Medicao

# Todos os valores nulos mapeados nas planilhas da Schulz
TOKENS_NULOS = {
    "", "-", "--", "---", "----", "n/a", "na", "null", "none", "nan",
    "#value!", "#valor!", "#ref!", "#div/0!", "#name?", "#nome?",
    "err:509", "###", "00/00/0000"
}

# Responsavel por ler cada linha de resultado da planilha (DIMENSION, NOMINAL, +TOL, -TOL, MEDIDA1, MEDIDA2)
# Faz a limpeza dos dados de acordo com as regras mapeadas no Desafio 1
# Grava o resultado na tabela medicoes
class MedicaoService:
    # Inicializacao
    def __init__(self, conexao: ConexaoBanco):
        self.conexao = conexao # conexao com o banco
        self.dao = MedicaoDAO(conexao) #instancia o objeto Medicao DAO

    # Metodo para limpeza e validacao de valores
    @staticmethod
    def limpar_nulo(valor):
        if valor is None:
            return None
        if isinstance(valor, str): # verifica se o valor informado é um string
            texto = re.sub(r"[\x00-\x1f\x7f]", "", valor).strip() # remove espacos
            if texto.lower() in TOKENS_NULOS:
                return None # verifica se o valor informado é um dos valores considerados nulos
            return texto # retorna o valor informado, do tipo string
        return valor # retorna valor informado, do tipo number

    # metodo para verificacao e padronizacao do nome da caracteristica
    def limpar_codigo_caracteristica(self, valor) -> str | None:
        limpo = self.limpar_nulo(valor) # realiza a limpeza dos espacos adicionais
        if limpo is None:
            return None # verifica se o valor informado é nulo
        sem_acento = unicodedata.normalize("NFKD", str(limpo)) # remove os acentos
        sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c)) 
        return re.sub(r"\s+", "_", sem_acento.strip()).upper() # substitui espacos por _ e converte todo o texto informado para maiusculas

    # Verificacao de valores numericos
    def limpar_numero(self, valor) -> float | None:
        if valor is None:
            return None
        if isinstance(valor, (int, float)):
            return round(float(valor), 7) # verifica se é um numero e converte para o tipo float, com até 7 casas decimais

        limpo = self.limpar_nulo(valor) # caso seja uma string, faz a limpeza de espacos adicionais
        if limpo is None:
            return None # verificar se o valor é nulo

        texto = str(limpo).replace("°", "").replace("mm", "").strip() # remove virgulas e substitui por ponto, e remove unidades de medida
        if "," in texto and "." in texto:
            texto = texto.replace(".", "").replace(",", ".") # remove pontos e substitui virgulas por ponto, respeitando a formatacao do tipo float
        elif "," in texto:
            texto = texto.replace(",", ".") # substitui virgulas por pontos, respeitando a formatacao do tipo float

        try:
            return round(float(texto), 7) # converte a string para o tipo float, arredondando o numero para ate 7 casas decimais
        except ValueError:
            return None # para tratamento de erros

    def salvar(
        self, equipamento_id: int, padrao_id: int, tecnico_id: int,
        dt_hora_iso: str, plano_medicao: str, codigo: str,
        parametro_bruto: str, nominal_bruto, tol_sup_bruto, tol_inf_bruto,
        meas1_bruto, meas2_bruto, unidade: str = "mm"
    ) -> tuple[Medicao | None, str | None]:
        # Validacao dos valores informados, aplicando as regras dos metodos auxiliares
        parametro = self.limpar_codigo_caracteristica(parametro_bruto)
        nominal = self.limpar_numero(nominal_bruto)
        tol_sup = self.limpar_numero(tol_sup_bruto)
        tol_inf = self.limpar_numero(tol_inf_bruto)
        m1 = self.limpar_numero(meas1_bruto)
        m2 = self.limpar_numero(meas2_bruto)

        if not parametro or nominal is None or m1 is None or m2 is None:
            # Validar se a linha contem valores validos
            return None, f"Linha ignorada ({parametro_bruto}): campo obrigatório nulo ou inválido."

        alerta = None
        if abs(m1 - m2) < 1e-9:
            # Verifica se a linha possui valores iguais para medida 1 e medida 2
            alerta = f"RN-10 [{parametro}]: Medida 1 e Medida 2 são idênticas ({m1:.4f})."

        media_obtida = round((m1 + m2) / 2.0, 7)
        _ = round(statistics.stdev([m1, m2]), 7)  # Calcula o desvio padrao apenas das linhas validas

        # Instancia o objeto Medicao
        medicao = Medicao(
            equipamentoId=equipamento_id,
            padraoId=padrao_id,
            tecnicoId=tecnico_id,
            dtHoraMedicao=dt_hora_iso,
            planoMedicao=self.limpar_nulo(plano_medicao),
            codigo=codigo,
            parametro=parametro,
            unidade=unidade,
            valorNominal=nominal,
            toleranciaSuperior=tol_sup,
            toleranciaInferior=tol_inf,
            medida1=m1,
            medida2=m2,
            valorObtido=media_obtida,
        )
        self.dao.inserir(medicao) # insere o objeto no banco de dados

        # Retorna o valor inserido e a mensagem de alerta
        return medicao, alerta