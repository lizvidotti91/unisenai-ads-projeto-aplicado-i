-- =====================================================================
-- Projeto Aplicado I — UniSENAI / ADS — Schulz S.A.
-- Entrega 02: Modelagem e Implementação de Banco de Dados (SQLite)
-- Arquivo : 03_banco.sql  (script DDL — 3 tabelas)
-- Tabelas : tecnico_solicitante, equipamento, medicao
-- Execução: sqlite3 schulz.db < 03_banco.sql
-- =====================================================================

-- O SQLite NÃO valida chaves estrangeiras por padrão: ativar em toda conexão.
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- 1. TECNICO_SOLICITANTE
--    Quem executa/confere/assina a calibração (técnico) ou quem pede o
--    serviço (solicitante). O campo "papel" distingue os perfis.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tecnico_solicitante (
    id_tecnico  INTEGER PRIMARY KEY,                      -- PK (autoincremento via rowid)
    matricula   TEXT    UNIQUE,                           -- opcional (solicitante externo pode não ter)
    nome        TEXT    NOT NULL,
    cargo       TEXT,                                     -- cargo/função na empresa
    papel       TEXT    NOT NULL
                CHECK (papel IN ('METROLOGISTA', 'SIGNATARIO', 'SOLICITANTE')),
    setor       TEXT,
    turno       TEXT
                CHECK (turno IS NULL OR turno IN ('MATUTINO', 'VESPERTINO', 'NOTURNO')),
    ativo       INTEGER NOT NULL DEFAULT 1
                CHECK (ativo IN (0, 1))
);

-- ---------------------------------------------------------------------
-- 2. EQUIPAMENTO
--    Cadastro único de máquinas (MMC) e instrumentos/dispositivos de
--    controle. Cada equipamento é cadastrado UMA vez e reutilizado em
--    todas as medições.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS equipamento (
    id_equipamento   INTEGER PRIMARY KEY,                 -- PK
    tag_equipamento  TEXT    NOT NULL UNIQUE,             -- identificação/TAG (ex.: código do padrão)
    tipo             TEXT    NOT NULL
                     CHECK (tipo IN ('MMC', 'INSTRUMENTO')),
    numero_serie     TEXT    NOT NULL UNIQUE,
    nome_equipamento TEXT    NOT NULL,                    -- nome/descrição do equipamento
    fabricante       TEXT    NOT NULL DEFAULT 'NAO INFORMADO',
    modelo           TEXT,
    faixa_medicao    TEXT,                                -- ex.: "700x1000x600 mm"
    drawing_no       TEXT,                                -- nº do desenho
    part_no          TEXT,                                -- nº da peça
    rastreabilidade  TEXT,                                -- certificado do padrão (evita "???")
    fk_solicitante_id INTEGER,                            -- FK -> dono/solicitante (NULL = equipamento interno)
    FOREIGN KEY (fk_solicitante_id)
        REFERENCES tecnico_solicitante (id_tecnico)
        ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- 3. MEDICAO
--    Uma linha por característica medida numa calibração.
--    Liga equipamento (calibrado e padrão MMC usado) e técnico.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medicao (
    id_medicao          INTEGER PRIMARY KEY,              -- PK
    fk_equipamento_id   INTEGER NOT NULL,                 -- FK -> equipamento calibrado
    fk_padrao_id        INTEGER,                          -- FK -> equipamento (MMC utilizada)
    fk_tecnico_id       INTEGER NOT NULL,                 -- FK -> técnico (metrologista)
    numero_certificado  TEXT,                             -- preenchido na emissão
    data_hora_medicao   TEXT    NOT NULL,                 -- ISO 8601: AAAA-MM-DD HH:MM:SS
    plano_medicao       TEXT,                             -- measurement plan do Calypso
    codigo              TEXT    NOT NULL,                 -- código da característica
    parametro           TEXT    NOT NULL,                 -- parâmetro medido
    eixo_referencia     TEXT,
    unidade             TEXT    NOT NULL DEFAULT 'mm'
                        CHECK (unidade IN ('mm', 'um', 'graus')),
    valor_nominal       REAL    NOT NULL,
    tolerancia_superior REAL,                             -- NULL = tolerância unilateral
    tolerancia_inferior REAL,
    medida_1            REAL    NOT NULL,                 -- 1ª medição
    medida_2            REAL,                             -- 2ª medição
    valor_obtido        REAL    NOT NULL,                 -- valor final (Actual)
    desvio              REAL    NOT NULL,                 -- valor_obtido - valor_nominal
    status              TEXT    NOT NULL DEFAULT 'PENDENTE'
                        CHECK (status IN ('APROVADO', 'REPROVADO', 'PENDENTE')),

    FOREIGN KEY (fk_equipamento_id) REFERENCES equipamento (id_equipamento)
        ON DELETE RESTRICT,
    FOREIGN KEY (fk_padrao_id)      REFERENCES equipamento (id_equipamento)
        ON DELETE RESTRICT,
    FOREIGN KEY (fk_tecnico_id)     REFERENCES tecnico_solicitante (id_tecnico)
        ON DELETE RESTRICT,

    -- integridade de domínio
    CHECK (tolerancia_superior IS NULL OR tolerancia_inferior IS NULL
           OR tolerancia_superior >= tolerancia_inferior),
    CHECK (abs(desvio - (valor_obtido - valor_nominal)) < 0.000001),

    -- impede a mesma característica duplicada na mesma calibração
    UNIQUE (fk_equipamento_id, data_hora_medicao, codigo)
);

-- Índices nas chaves estrangeiras (consultas e histórico por equipamento)
CREATE INDEX IF NOT EXISTS idx_equipamento_solicitante ON equipamento (fk_solicitante_id);
CREATE INDEX IF NOT EXISTS idx_medicao_equipamento     ON medicao (fk_equipamento_id);
CREATE INDEX IF NOT EXISTS idx_medicao_tecnico         ON medicao (fk_tecnico_id);