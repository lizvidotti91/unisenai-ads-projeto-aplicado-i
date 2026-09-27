-- Habilitar a verificação de Chaves Estrangeiras no SQLite
PRAGMA foreign_keys = ON;

-- -----------------------------------------------------
-- 1. Tabela: METROLOGISTA
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS metrologista (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula VARCHAR(30) NOT NULL UNIQUE,
    nome_metrologista VARCHAR(120) NOT NULL,
    turno VARCHAR(20) CHECK (turno IN ('MATUTINO', 'VESPERTINO', 'NOTURNO') OR turno IS NULL)
);

-- -----------------------------------------------------
-- 2. Tabela: INSTRUMENTO
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS instrumento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_equipamento CHAR(6) NOT NULL UNIQUE,
    numero_serie VARCHAR(60) NOT NULL UNIQUE,
    fabricante VARCHAR(120) DEFAULT 'NÃO INFORMADO',
    drawing_no VARCHAR(60),
    part_no VARCHAR(60),
    setor_solicitante VARCHAR(60) NOT NULL DEFAULT 'NÃO INFORMADO'
);

-- -----------------------------------------------------
-- 3. Tabela: MEDICAO_CERTIFICADO
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS medicao_certificado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_certificado VARCHAR(30) NOT NULL UNIQUE,
    
    -- Dados da Característica e Medição
    nome_caracteristica VARCHAR(60) NOT NULL,
    eixo_referencia VARCHAR(20),
    valor_nominal DECIMAL(12,7) NOT NULL,
    tolerancia_superior DECIMAL(12,7) NOT NULL,
    tolerancia_inferior DECIMAL(12,7) NOT NULL,
    valor_atual DECIMAL(12,7) NOT NULL,
    desvio DECIMAL(12,7) NOT NULL,
    status_conformidade VARCHAR(20) NOT NULL CHECK (status_conformidade IN ('CONFORME', 'NAO_CONFORME', 'PENDENTE')),
    
    -- Dados Metrológicos Adicionais (Entrega 01)
    incerteza_expandida DECIMAL(12,7),
    fator_k DECIMAL(5,2) DEFAULT 2.00,
    
    -- Dados da Execução e Equipamento de Medição
    codigo_mmc VARCHAR(30),
    measurement_plan VARCHAR(60),
    hora_medicao TIME,
    
    -- Dados do Certificado e Auditoria
    data_calibracao DATE NOT NULL DEFAULT CURRENT_DATE,
    norma_referencia VARCHAR(60) NOT NULL DEFAULT 'ABNT NBR ISO/IEC 17025:2017',
    signatario VARCHAR(120),
    observacoes TEXT,
    
    -- Chaves Estrangeiras para as 3 entidades
    fk_metrologista_id INTEGER NOT NULL,
    fk_instrumento_id INTEGER NOT NULL,
    
    FOREIGN KEY (fk_metrologista_id) REFERENCES metrologista (id) ON DELETE RESTRICT,
    FOREIGN KEY (fk_instrumento_id) REFERENCES instrumento (id) ON DELETE RESTRICT
);