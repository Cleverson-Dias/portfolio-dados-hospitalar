-- ============================================================================
-- Projeto 2 - Análise com SQL (PostgreSQL)
-- 03: views reutilizáveis
--
-- As views guardam os cálculos mais usados (permanência, indicadores por unidade
-- e por mês, ocupação). As consultas do arquivo 04 e o dashboard do Projeto 3
-- partem delas, em vez de repetir a mesma lógica.
-- ============================================================================
\encoding UTF8

-- Base detalhada: internação + unidade + campos calculados
CREATE OR REPLACE VIEW vw_internacoes_detalhe AS
SELECT
    i.id_internacao,
    i.id_paciente,
    u.id_unidade,
    u.nome_unidade,
    i.id_leito,
    i.data_entrada,
    i.data_saida,
    (EXTRACT(EPOCH FROM (i.data_saida - i.data_entrada)) / 86400.0)::numeric AS permanencia_dias,
    DATE_TRUNC('month', i.data_entrada)::date                                AS mes_entrada,
    i.tempo_espera_min,
    i.idade,
    CASE
        WHEN i.idade IS NULL THEN 'Não informada'
        WHEN i.idade < 12    THEN '0-11'
        WHEN i.idade < 18    THEN '12-17'
        WHEN i.idade < 40    THEN '18-39'
        WHEN i.idade < 60    THEN '40-59'
        ELSE '60+'
    END AS faixa_etaria,
    i.sexo,
    i.convenio,
    i.infeccao_hospitalar,
    i.desfecho
FROM internacoes i
JOIN unidades u ON u.id_unidade = i.id_unidade;

-- Indicadores principais por unidade
CREATE OR REPLACE VIEW vw_indicadores_unidade AS
SELECT
    id_unidade,
    nome_unidade,
    COUNT(*)                                                        AS internacoes,
    ROUND(AVG(permanencia_dias), 1)                                 AS permanencia_media_dias,
    ROUND(AVG(tempo_espera_min), 1)                                 AS espera_media_min,
    ROUND(100.0 * AVG(infeccao_hospitalar), 1)                      AS taxa_infeccao_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE desfecho = 'Óbito') / COUNT(*), 1) AS taxa_obito_pct
FROM vw_internacoes_detalhe
GROUP BY id_unidade, nome_unidade;

-- Indicadores por mês (todas as unidades juntas)
CREATE OR REPLACE VIEW vw_indicadores_mensais AS
SELECT
    mes_entrada,
    COUNT(*)                                   AS internacoes,
    ROUND(AVG(permanencia_dias), 1)            AS permanencia_media_dias,
    ROUND(AVG(tempo_espera_min), 1)            AS espera_media_min,
    SUM(infeccao_hospitalar)                   AS internacoes_com_infeccao,
    ROUND(100.0 * AVG(infeccao_hospitalar), 1) AS taxa_infeccao_pct
FROM vw_internacoes_detalhe
GROUP BY mes_entrada;

-- Ocupação estimada: leitos-dia ocupados / leitos-dia disponíveis no período
CREATE OR REPLACE VIEW vw_ocupacao_unidade AS
WITH periodo AS (
    SELECT (MAX(data_entrada)::date - MIN(data_entrada)::date + 1) AS dias
    FROM internacoes
)
SELECT
    u.id_unidade,
    u.nome_unidade,
    u.capacidade_leitos,
    ROUND(SUM(d.permanencia_dias))                                                   AS leitos_dia_ocupados,
    ROUND(100.0 * SUM(d.permanencia_dias) / (u.capacidade_leitos * p.dias), 1)       AS ocupacao_estimada_pct
FROM unidades u
JOIN vw_internacoes_detalhe d ON d.id_unidade = u.id_unidade
CROSS JOIN periodo p
GROUP BY u.id_unidade, u.nome_unidade, u.capacidade_leitos, p.dias;
