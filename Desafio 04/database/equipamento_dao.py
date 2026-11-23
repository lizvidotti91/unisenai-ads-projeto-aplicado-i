from classes.Equipamento import Equipamento
from .conexao import ConexaoBanco


class EquipamentoDAO:
    def __init__(self, conexao: ConexaoBanco):
        self.conexao = conexao

    def inserir(self, equipamento: Equipamento):
        sql = (
            "INSERT INTO equipamentos "
            "(tagEquipamento, tipo, numeroSerie, nomeEquipamento, fabricante, "
            " modelo, faixaMedicao, drawningNo, partNo, rastreabilidade, solicitanteId) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        params = (
            equipamento.tagEquipamento,
            equipamento.tipo,
            equipamento.numeroSerie,
            equipamento.nomeEquipamento,
            equipamento.fabricante,
            equipamento.modelo,
            equipamento.faixaMedicao,
            equipamento.drawningNo,
            equipamento.partNo,
            equipamento.rastreabilidade,
            equipamento.solicitanteId,
        )
        novo_id = self.conexao.executar(sql, params, commit=True)
        equipamento.idEquipamento = novo_id
        return novo_id

    def buscar_por_id(self, id_equipamento: int):
        sql = "SELECT * FROM equipamentos WHERE idEquipamento = ?"
        row = self.conexao.consultar_um(sql, (id_equipamento,))
        return self._row_para_objeto(row) if row else None

    def listar_todos(self):
        sql = "SELECT * FROM equipamentos ORDER BY tagEquipamento"
        rows = self.conexao.consultar(sql)
        return [self._row_para_objeto(r) for r in rows]

    def buscar_por_tag(self, tag: str):
        sql = "SELECT * FROM equipamentos WHERE tagEquipamento LIKE ? ORDER BY tagEquipamento"
        rows = self.conexao.consultar(sql, (f"%{tag}%",))
        return [self._row_para_objeto(r) for r in rows]

    def listar_por_solicitante(self, id_solicitante: int):
        sql = "SELECT * FROM equipamentos WHERE solicitanteId = ? ORDER BY tagEquipamento"
        rows = self.conexao.consultar(sql, (id_solicitante,))
        return [self._row_para_objeto(r) for r in rows]

    def atualizar(self, equipamento: Equipamento):
        if equipamento.idEquipamento is None:
            raise ValueError("Não é possível atualizar um equipamento sem idEquipamento.")

        sql = (
            "UPDATE equipamentos SET "
            "tagEquipamento = ?, tipo = ?, numeroSerie = ?, nomeEquipamento = ?, "
            "fabricante = ?, modelo = ?, faixaMedicao = ?, drawningNo = ?, "
            "partNo = ?, rastreabilidade = ?, solicitanteId = ? "
            "WHERE idEquipamento = ?"
        )
        params = (
            equipamento.tagEquipamento,
            equipamento.tipo,
            equipamento.numeroSerie,
            equipamento.nomeEquipamento,
            equipamento.fabricante,
            equipamento.modelo,
            equipamento.faixaMedicao,
            equipamento.drawningNo,
            equipamento.partNo,
            equipamento.rastreabilidade,
            equipamento.solicitanteId,
            equipamento.idEquipamento,
        )
        self.conexao.executar(sql, params, commit=True)
        return True

    def deletar(self, id_equipamento: int):
        sql = "DELETE FROM equipamentos WHERE idEquipamento = ?"
        self.conexao.executar(sql, (id_equipamento,), commit=True)
        return True

    @staticmethod
    def _row_para_objeto(row):
        return Equipamento(
            tagEquipamento=row["tagEquipamento"],
            tipo=row["tipo"],
            numeroSerie=row["numeroSerie"],
            nomeEquipamento=row["nomeEquipamento"],
            fabricante=row["fabricante"],
            modelo=row["modelo"],
            faixaMedicao=row["faixaMedicao"],
            drawningNo=row["drawningNo"],
            partNo=row["partNo"],
            rastreabilidade=row["rastreabilidade"],
            solicitanteId=row["solicitanteId"],
            idEquipamento=row["idEquipamento"],
        )
