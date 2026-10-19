-- ============================================================================
-- Projeto 2 - Análise com SQL (PostgreSQL)
-- 02: carrega os CSVs da pasta dados/ nas tabelas
--
-- IMPORTANTE: execute a partir da PASTA RAIZ do repositório, porque os caminhos
-- abaixo são relativos a ela (dados/...). Exemplo:
--   psql -U postgres -d hospital -f 02-sql-analise/02_carregar_dados.sql
--
-- O \copy lê o arquivo no seu computador (não precisa de permissão de superusuário).
-- ============================================================================
\encoding UTF8

\copy unidades (id_unidade, nome_unidade, capacidade_leitos) FROM 'dados/unidades.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

\copy leitos (id_leito, id_unidade, numero_leito) FROM 'dados/leitos.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

\copy internacoes (id_internacao, id_paciente, id_unidade, id_leito, data_entrada, data_saida, tempo_espera_min, idade, sexo, convenio, infeccao_hospitalar, desfecho) FROM 'dados/internacoes.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

-- Conferência: quantas linhas entraram em cada tabela
SELECT 'unidades'    AS tabela, COUNT(*) AS linhas FROM unidades
UNION ALL
SELECT 'leitos',      COUNT(*) FROM leitos
UNION ALL
SELECT 'internacoes', COUNT(*) FROM internacoes;
