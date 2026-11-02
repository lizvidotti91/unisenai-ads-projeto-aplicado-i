from classes.Medicao import Medicao
from .conexao import ConexaoBanco


class MedicaoDAO:
    def __init__(self, conexao: ConexaoBanco):
        self.conexao = conexao

    def inserir(self, medicao: Medicao) -> int:
        sql = (
            "INSERT INTO medicoes "
            "(equipamentoId, padraoId, tecnicoId, numeroCertificacao, dtHoramedicao, "
            " planoMedicao, codigo, parametro, eixoReferencia, unidade, "
            " valorNominal, toleranciaSuperior, toleranciaInferior, "
            " medida1, medida2, valorObtido, desvio, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        params = (
            medicao.equipamentoId,
            medicao.padraoId,
            medicao.tecnicoId,
            medicao.numeroCertificacao,
            medicao.dtHoramedicao,
            medicao.planoMedicao,
            medicao.codigo,
            medicao.parametro,
            medicao.eixoReferencia,
            medicao.unidade,
            medicao.valorNominal,
            medicao.toleranciaSuperior,
            medicao.toleranciaInferior,
            medicao.medida1,
            medicao.medida2,
            medicao.valorObtido,
            medicao.desvio,
            medicao.status,
        )
        novo_id = self.conexao.executar(sql, params, commit=True)
        medicao.idMedicao = novo_id
        return novo_id

    def buscar_por_id(self, id_medicao: int):
        sql = "SELECT * FROM medicoes WHERE idMedicao = ?"
        row = self.conexao.consultar_um(sql, (id_medicao,))
        return self._row_para_objeto(row) if row else None

    def listar_todos(self):
        sql = "SELECT * FROM medicoes ORDER BY dtHoramedicao DESC"
        rows = self.conexao.consultar(sql)
        return [self._row_para_objeto(r) for r in rows]

    def listar_por_equipamento(self, id_equipamento: int):
        sql = (
            "SELECT * FROM medicoes WHERE equipamentoId = ? "
            "ORDER BY dtHoramedicao DESC"
        )
        rows = self.conexao.consultar(sql, (id_equipamento,))
        return [self._row_para_objeto(r) for r in rows]

    def listar_por_tecnico(self, id_tecnico: int):
        sql = (
            "SELECT * FROM medicoes WHERE tecnicoId = ? "
            "ORDER BY dtHoramedicao DESC"
        )
        rows = self.conexao.consultar(sql, (id_tecnico,))
        return [self._row_para_objeto(r) for r in rows]

    def listar_por_status(self, status: str):
        sql = (
            "SELECT * FROM medicoes WHERE UPPER(status) = UPPER(?) "
            "ORDER BY dtHoramedicao DESC"
        )
        rows = self.conexao.consultar(sql, (status,))
        return [self._row_para_objeto(r) for r in rows]

    def atualizar(self, medicao: Medicao):
        if medicao.idMedicao is None:
            raise ValueError("Não é possível atualizar uma medição sem idMedicao.")

        sql = (
            "UPDATE medicoes SET "
            "equipamentoId = ?, padraoId = ?, tecnicoId = ?, "
            "numeroCertificacao = ?, dtHoramedicao = ?, planoMedicao = ?, "
            "codigo = ?, parametro = ?, eixoReferencia = ?, unidade = ?, "
            "valorNominal = ?, toleranciaSuperior = ?, toleranciaInferior = ?, "
            "medida1 = ?, medida2 = ?, valorObtido = ?, desvio = ?, status = ? "
            "WHERE idMedicao = ?"
        )
        params = (
            medicao.equipamentoId,
            medicao.padraoId,
            medicao.tecnicoId,
            medicao.numeroCertificacao,
            medicao.dtHoramedicao,
            medicao.planoMedicao,
            medicao.codigo,
            medicao.parametro,
            medicao.eixoReferencia,
            medicao.unidade,
            medicao.valorNominal,
            medicao.toleranciaSuperior,
            medicao.toleranciaInferior,
            medicao.medida1,
            medicao.medida2,
            medicao.valorObtido,
            medicao.desvio,
            medicao.status,
            medicao.idMedicao,
        )
        self.conexao.executar(sql, params, commit=True)
        return True

    def deletar(self, id_medicao: int):
        sql = "DELETE FROM medicoes WHERE idMedicao = ?"
        self.conexao.executar(sql, (id_medicao,), commit=True)
        return True

    @staticmethod
    def _row_para_objeto(row):
        return Medicao(
            equipamentoId=row["equipamentoId"],
            tecnicoId=row["tecnicoId"],
            codigo=row["codigo"],
            parametro=row["parametro"],
            valorNominal=row["valorNominal"],
            medida1=row["medida1"],
            valorObtido=row["valorObtido"],
            padraoId=row["padraoId"],
            numeroCertificacao=row["numeroCertificacao"],
            planoMedicao=row["planoMedicao"],
            eixoReferencia=row["eixoReferencia"],
            unidade=row["unidade"],
            toleranciaSuperior=row["toleranciaSuperior"],
            toleranciaInferior=row["toleranciaInferior"],
            medida2=row["medida2"],
            status=row["status"],
            idMedicao=row["idMedicao"],
            dtHoraMedicao=row["dtHoramedicao"],
        )
