import os
import sqlite3
from sqlite3 import Error as SqliteError

# Schema
_SCHEMA_SQL = """
-- Tabela de Técnicos / Solicitantes
CREATE TABLE IF NOT EXISTS tecnicos (
    idTecnico   INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula   TEXT    UNIQUE,
    nome        TEXT    NOT NULL,
    cargo       TEXT,
    papel       TEXT    NOT NULL
                CHECK (papel IN ('METROLOGISTA', 'SIGNATARIO', 'SOLICITANTE')),
    setor       TEXT,
    turno       TEXT
                CHECK (turno IS NULL OR turno IN ('MATUTINO', 'VESPERTINO', 'NOTURNO')),
    ativo       INTEGER NOT NULL DEFAULT 1
                CHECK (ativo IN (0, 1))   -- 0 = inativo, 1 = ativo
);

-- Tabela de Equipamentos
CREATE TABLE IF NOT EXISTS equipamentos (
    idEquipamento  INTEGER PRIMARY KEY AUTOINCREMENT,
    tagEquipamento TEXT    NOT NULL UNIQUE,
    tipo           TEXT    NOT NULL
                   CHECK (tipo IN ('MMC', 'INSTRUMENTO')),
    numeroSerie    TEXT    NOT NULL UNIQUE,
    nomeEquipamento TEXT   NOT NULL,
    fabricante     TEXT    NOT NULL DEFAULT 'NAO INFORMADO',
    modelo         TEXT,
    faixaMedicao   TEXT,
    drawningNo     TEXT,
    partNo         TEXT,
    rastreabilidade TEXT,
    solicitanteId  INTEGER,
    FOREIGN KEY (solicitanteId) REFERENCES tecnicos(idTecnico)
        ON DELETE SET NULL
);

-- Tabela de Medições
CREATE TABLE IF NOT EXISTS medicoes (
    idMedicao          INTEGER PRIMARY KEY AUTOINCREMENT,
    equipamentoId      INTEGER NOT NULL,
    padraoId           INTEGER,           -- FK para equipamentos (padrão de calibração)
    tecnicoId          INTEGER NOT NULL,
    numeroCertificacao TEXT,
    dtHoramedicao      TEXT    NOT NULL,  -- ISO 8601: 'YYYY-MM-DD HH:MM:SS'
    planoMedicao       TEXT,
    codigo             TEXT    NOT NULL,
    parametro          TEXT    NOT NULL,
    eixoReferencia     TEXT,
    unidade            TEXT    NOT NULL
                       CHECK (unidade IN ('mm', 'um', 'graus')),
    valorNominal       REAL    NOT NULL,
    toleranciaSuperior REAL,
    toleranciaInferior REAL,
    medida1            REAL    NOT NULL,
    medida2            REAL,
    valorObtido        REAL    NOT NULL,
    desvio             REAL    NOT NULL,
    status             TEXT    NOT NULL DEFAULT 'PENDENTE'
                       CHECK (status IN ('APROVADO', 'REPROVADO', 'PENDENTE')),
    FOREIGN KEY (equipamentoId) REFERENCES equipamentos(idEquipamento)
        ON DELETE CASCADE,
    FOREIGN KEY (padraoId) REFERENCES equipamentos(idEquipamento)
        ON DELETE SET NULL,
    FOREIGN KEY (tecnicoId) REFERENCES tecnicos(idTecnico)
        ON DELETE RESTRICT,

    -- integridade de domínio (mesmas regras do banco da AV02)
    CHECK (toleranciaSuperior IS NULL OR toleranciaInferior IS NULL
           OR toleranciaSuperior >= toleranciaInferior),
    CHECK (abs(desvio - (valorObtido - valorNominal)) < 0.000001)
);
"""


class ConexaoBanco:
    def __init__(self, caminho_banco: str = ""):
        if not caminho_banco:
            raiz_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            caminho_banco = os.path.join(raiz_projeto, "metrologia.db")
        self.caminho_banco = caminho_banco
        self._conexao = None


    def conectar(self):
        if self._conexao is None:
            try:
                self._conexao = sqlite3.connect(self.caminho_banco)
                self._conexao.row_factory = sqlite3.Row
                self._conexao.execute("PRAGMA foreign_keys = ON;")
            except SqliteError as e:
                raise RuntimeError(f"Falha ao conectar ao banco '{self.caminho_banco}': {e}") from e
        return self._conexao

    def fechar(self):
        if self._conexao is not None:
            try:
                self._conexao.close()
            except SqliteError:
                pass
            finally:
                self._conexao = None

    def __enter__(self):
        self.conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and self._conexao is not None:
            try:
                self._conexao.rollback()
            except SqliteError:
                pass
        self.fechar()

    def executar(self, sql: str, params: tuple = (), commit: bool = True):
        conexao = self.conectar()
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, params)
            if commit:
                conexao.commit()
            return cursor.lastrowid
        except SqliteError as e:
            conexao.rollback()
            raise RuntimeError(f"Erro ao executar SQL: {e}\nSQL: {sql}\nParams: {params}") from e
        finally:
            cursor.close()

    def consultar(self, sql: str, params: tuple = ()):
        conexao = self.conectar()
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        except SqliteError as e:
            raise RuntimeError(f"Erro ao consultar: {e}\nSQL: {sql}\nParams: {params}") from e
        finally:
            cursor.close()

    def consultar_um(self, sql: str, params: tuple = ()):
        resultados = self.consultar(sql, params)
        return resultados[0] if resultados else None


    def criar_tabelas(self):
        conexao = self.conectar()
        cursor = conexao.cursor()
        try:
            cursor.executescript(_SCHEMA_SQL)
            conexao.commit()
        except SqliteError as e:
            conexao.rollback()
            raise RuntimeError(f"Erro ao criar tabelas: {e}") from e
        finally:
            cursor.close()
