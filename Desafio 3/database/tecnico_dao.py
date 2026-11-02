from classes.TecnicoSolicitante import TecnicoSolicitante
from .conexao import ConexaoBanco


_COLUNAS = [
    "matricula", "nome", "cargo", "papel", "setor", "turno", "ativo"
]


class TecnicoDAO:
    def __init__(self, conexao: ConexaoBanco):
        self.conexao = conexao

    def inserir(self, tecnico: TecnicoSolicitante):
        sql = (
            "INSERT INTO tecnicos "
            "(matricula, nome, cargo, papel, setor, turno, ativo) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)"
        )
        params = (
            tecnico.matricula,
            tecnico.nome,
            tecnico.cargo,
            tecnico.papel,
            tecnico.setor,
            tecnico.turno,
            tecnico.ativo,
        )
        novo_id = self.conexao.executar(sql, params, commit=True)
        tecnico.idTecnico = novo_id
        return novo_id

    def buscar_por_id(self, id_tecnico: int):
        sql = "SELECT * FROM tecnicos WHERE idTecnico = ?"
        row = self.conexao.consultar_um(sql, (id_tecnico,))
        return self._row_para_objeto(row) if row else None

    def listar_todos(self):
        sql = "SELECT * FROM tecnicos ORDER BY nome"
        rows = self.conexao.consultar(sql)
        return [self._row_para_objeto(r) for r in rows]

    def listar_ativos(self):
        sql = "SELECT * FROM tecnicos WHERE ativo = 1 ORDER BY nome"
        rows = self.conexao.consultar(sql)
        return [self._row_para_objeto(r) for r in rows]

    def buscar_por_papel(self, papel: str) -> list[TecnicoSolicitante]:
        sql = "SELECT * FROM tecnicos WHERE UPPER(papel) = UPPER(?) ORDER BY nome"
        rows = self.conexao.consultar(sql, (papel,))
        return [self._row_para_objeto(r) for r in rows]

    def atualizar(self, tecnico: TecnicoSolicitante) -> bool:
        if tecnico.idTecnico is None:
            raise ValueError("Não é possível atualizar um técnico sem idTecnico.")

        sql = (
            "UPDATE tecnicos SET "
            "matricula = ?, nome = ?, cargo = ?, papel = ?, "
            "setor = ?, turno = ?, ativo = ? "
            "WHERE idTecnico = ?"
        )
        params = (
            tecnico.matricula,
            tecnico.nome,
            tecnico.cargo,
            tecnico.papel,
            tecnico.setor,
            tecnico.turno,
            tecnico.ativo,
            tecnico.idTecnico,
        )
        self.conexao.executar(sql, params, commit=True)
        return True

    def deletar(self, id_tecnico: int) -> bool:
        sql = "DELETE FROM tecnicos WHERE idTecnico = ?"
        self.conexao.executar(sql, (id_tecnico,), commit=True)
        return True

    @staticmethod
    def _row_para_objeto(row) -> TecnicoSolicitante:
        return TecnicoSolicitante(
            matricula=row["matricula"],
            nome=row["nome"],
            cargo=row["cargo"],
            papel=row["papel"],
            setor=row["setor"],
            turno=row["turno"],
            ativo=row["ativo"],
            idTecnico=row["idTecnico"],
        )
