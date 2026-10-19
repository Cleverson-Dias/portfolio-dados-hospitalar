-- ============================================================================
-- Projeto 2 - Análise com SQL (PostgreSQL)
-- 01: cria as tabelas do banco "hospital"
--
-- Dados FICTÍCIOS (gerados por scripts/gerar_dados.py).
-- Pode ser executado várias vezes: recria tudo do zero.
-- ============================================================================
\encoding UTF8

DROP TABLE IF EXISTS internacoes CASCADE;
DROP TABLE IF EXISTS leitos      CASCADE;
DROP TABLE IF EXISTS unidades    CASCADE;

-- Unidades hospitalares (UTI, clínicas, pronto-socorro...)
CREATE TABLE unidades (
    id_unidade        INTEGER PRIMARY KEY,
    nome_unidade      TEXT    NOT NULL UNIQUE,
    capacidade_leitos INTEGER NOT NULL CHECK (capacidade_leitos > 0)
);

-- Leitos de cada unidade
CREATE TABLE leitos (
    id_leito     INTEGER PRIMARY KEY,
    id_unidade   INTEGER NOT NULL REFERENCES unidades (id_unidade),
    numero_leito TEXT    NOT NULL,
    UNIQUE (id_unidade, numero_leito)
);

-- Internações: uma linha por internação
CREATE TABLE internacoes (
    id_internacao       INTEGER   PRIMARY KEY,
    id_paciente         INTEGER   NOT NULL,
    id_unidade          INTEGER   NOT NULL REFERENCES unidades (id_unidade),
    id_leito            INTEGER   NOT NULL REFERENCES leitos (id_leito),
    data_entrada        TIMESTAMP NOT NULL,
    data_saida          TIMESTAMP NOT NULL,
    tempo_espera_min    INTEGER   NOT NULL CHECK (tempo_espera_min >= 0),
    idade               INTEGER   CHECK (idade BETWEEN 0 AND 110),
    sexo                CHAR(1)   CHECK (sexo IN ('F', 'M')),
    convenio            TEXT,
    infeccao_hospitalar SMALLINT  NOT NULL CHECK (infeccao_hospitalar IN (0, 1)),
    desfecho            TEXT      NOT NULL CHECK (desfecho IN ('Alta', 'Transferência', 'Óbito')),
    CHECK (data_saida > data_entrada)
);

-- Índices para as colunas mais usadas em filtros e junções
CREATE INDEX idx_internacoes_unidade ON internacoes (id_unidade);
CREATE INDEX idx_internacoes_leito   ON internacoes (id_leito);
CREATE INDEX idx_internacoes_entrada ON internacoes (data_entrada);
