-- Habilitar verificação de Chaves Estrangeiras no SQLite
PRAGMA foreign_keys = ON;

-- -----------------------------------------------------
-- 1. Tabela: FORNECEDOR_SETOR
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS fornecedor_setor (
    id VARCHAR(20) NOT NULL PRIMARY KEY,
    sigla_fornecedor VARCHAR(30) NOT NULL,
    setor VARCHAR(60) NOT NULL,
    responsavel_cadastro VARCHAR(120) NOT NULL
);

-- -----------------------------------------------------
-- 2. Tabela: INSTRUMENTO
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS instrumento (
    id VARCHAR(20) NOT NULL PRIMARY KEY,
    tag_equipamento CHAR(6) NOT NULL UNIQUE,
    numero_serie VARCHAR(60) NOT NULL UNIQUE,
    fabricante VARCHAR(120) DEFAULT 'NÃO INFORMADO',
    drawing_no VARCHAR(60),
    part_no VARCHAR(60),
    fk_fornecedor_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (fk_fornecedor_id) REFERENCES fornecedor_setor (id) ON DELETE RESTRICT
);

-- -----------------------------------------------------
-- 3. Tabela: METROLOGISTA
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS metrologista (
    id VARCHAR(20) NOT NULL PRIMARY KEY,
    matricula VARCHAR(30) NOT NULL UNIQUE,
    nome_metrologista VARCHAR(120) NOT NULL,
    turno VARCHAR(20) CHECK (turno IN ('MATUTINO', 'VESPERTINO', 'NOTURNO') OR turno IS NULL)
);

-- -----------------------------------------------------
-- 4. Tabela: MAQUINA_MMC
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS maquina_mmc (
    id VARCHAR(20) NOT NULL PRIMARY KEY,
    codigo_mmc VARCHAR(30) NOT NULL UNIQUE,
    measurement_plan VARCHAR(60),
    hora_medicao TIME
);

-- -----------------------------------------------------
-- 5. Tabela: CERTIFICADO_CALIBRACAO
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS certificado_calibracao (
    id VARCHAR(20) NOT NULL PRIMARY KEY,
    numero_certificado VARCHAR(30) NOT NULL UNIQUE,
    data_calibracao DATE NOT NULL DEFAULT CURRENT_DATE,
    status_conformidade VARCHAR(20) NOT NULL CHECK (status_conformidade IN ('CONFORME', 'NAO_CONFORME', 'PENDENTE')),
    fk_metrologista_id VARCHAR(20) NOT NULL,
    fk_instrumento_id VARCHAR(20) NOT NULL,
    fk_mmc_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (fk_metrologista_id) REFERENCES metrologista (id) ON DELETE RESTRICT,
    FOREIGN KEY (fk_instrumento_id) REFERENCES instrumento (id) ON DELETE RESTRICT,
    FOREIGN KEY (fk_mmc_id) REFERENCES maquina_mmc (id) ON DELETE RESTRICT
);

-- -----------------------------------------------------
-- 6. Tabela: MEDICAO_CARACTERISTICA
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS medicao_caracteristica (
    id VARCHAR(20) NOT NULL PRIMARY KEY,
    nome_caracteristica VARCHAR(60) NOT NULL,
    eixo_referencia VARCHAR(20),
    valor_nominal DECIMAL(12,7) NOT NULL,
    tolerancia_superior DECIMAL(12,7) NOT NULL,
    tolerancia_inferior DECIMAL(12,7) NOT NULL,
    valor_atual DECIMAL(12,7) NOT NULL,
    desvio DECIMAL(12,7) NOT NULL,
    fk_certificado_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (fk_certificado_id) REFERENCES certificado_calibracao (id) ON DELETE RESTRICT
);

-- -----------------------------------------------------
-- 7. Tabela: INCERTEZA_MEDICAO
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS incerteza_medicao (
    id VARCHAR(20) NOT NULL PRIMARY KEY,
    incerteza_expandida DECIMAL(12,7) NOT NULL,
    fator_k DECIMAL(5,2) DEFAULT 2.00,
    fk_medicao_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (fk_medicao_id) REFERENCES medicao_caracteristica (id) ON DELETE RESTRICT
);