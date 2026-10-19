-- ============================================================================
-- Projeto 2 - Análise com SQL (PostgreSQL)
-- 04: perguntas de negócio respondidas com consultas
--
-- Técnicas usadas: JOIN, GROUP BY, FILTER, CTE (WITH), funções de janela
-- (RANK, LAG, SUM OVER), PERCENTILE_CONT e CASE.
-- ============================================================================
\encoding UTF8


-- ----------------------------------------------------------------------------
-- 1) Quais unidades têm maior tempo médio de internação?
--    Compara cada unidade com a média geral do hospital.
-- ----------------------------------------------------------------------------
SELECT
    i.nome_unidade,
    i.internacoes,
    i.permanencia_media_dias,
    ROUND(i.permanencia_media_dias - g.media, 1) AS diferenca_para_media_hospital,
    RANK() OVER (ORDER BY i.permanencia_media_dias DESC) AS ranking
FROM vw_indicadores_unidade i
CROSS JOIN (SELECT AVG(permanencia_dias) AS media FROM vw_internacoes_detalhe) g
ORDER BY ranking;


-- ----------------------------------------------------------------------------
-- 2) Onde estão as infecções hospitalares?
--    Taxa por unidade e quanto tempo a mais ficam os pacientes que se infectaram.
--    (Mostra associação entre infecção e permanência, não prova causa.)
-- ----------------------------------------------------------------------------
SELECT
    nome_unidade,
    COUNT(*) FILTER (WHERE infeccao_hospitalar = 1)                                  AS com_infeccao,
    ROUND(100.0 * COUNT(*) FILTER (WHERE infeccao_hospitalar = 1) / COUNT(*), 1)     AS taxa_infeccao_pct,
    ROUND(AVG(permanencia_dias) FILTER (WHERE infeccao_hospitalar = 1), 1)           AS permanencia_com_infeccao,
    ROUND(AVG(permanencia_dias) FILTER (WHERE infeccao_hospitalar = 0), 1)           AS permanencia_sem_infeccao
FROM vw_internacoes_detalhe
GROUP BY nome_unidade
ORDER BY taxa_infeccao_pct DESC;


-- ----------------------------------------------------------------------------
-- 3) Quem espera mais para ser atendido?
--    Média, percentil 90 (os casos mais demorados) e % de esperas acima de 60 min.
-- ----------------------------------------------------------------------------
SELECT
    nome_unidade,
    ROUND(AVG(tempo_espera_min), 0)                                                  AS espera_media_min,
    ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY tempo_espera_min)::numeric, 0) AS espera_p90_min,
    ROUND(100.0 * COUNT(*) FILTER (WHERE tempo_espera_min > 60) / COUNT(*), 1)       AS pct_espera_acima_60min
FROM vw_internacoes_detalhe
GROUP BY nome_unidade
ORDER BY espera_media_min DESC;


-- ----------------------------------------------------------------------------
-- 4) Como evoluem as internações mês a mês?
--    Variação percentual contra o mês anterior (função de janela LAG).
-- ----------------------------------------------------------------------------
WITH mensal AS (
    SELECT
        mes_entrada,
        internacoes,
        taxa_infeccao_pct,
        LAG(internacoes) OVER (ORDER BY mes_entrada) AS internacoes_mes_anterior
    FROM vw_indicadores_mensais
)
SELECT
    TO_CHAR(mes_entrada, 'YYYY-MM') AS mes,
    internacoes,
    internacoes_mes_anterior,
    ROUND(100.0 * (internacoes - internacoes_mes_anterior) / NULLIF(internacoes_mes_anterior, 0), 1) AS variacao_pct,
    taxa_infeccao_pct
FROM mensal
ORDER BY mes_entrada;


-- ----------------------------------------------------------------------------
-- 5) Como a faixa etária se relaciona com a permanência e com os óbitos?
-- ----------------------------------------------------------------------------
SELECT
    faixa_etaria,
    COUNT(*)                                                                    AS internacoes,
    ROUND(AVG(permanencia_dias), 1)                                             AS permanencia_media_dias,
    ROUND(100.0 * COUNT(*) FILTER (WHERE desfecho = 'Óbito') / COUNT(*), 1)     AS taxa_obito_pct
FROM vw_internacoes_detalhe
GROUP BY faixa_etaria
ORDER BY MIN(COALESCE(idade, 999));


-- ----------------------------------------------------------------------------
-- 6) Qual a ocupação estimada de cada unidade?
--    Leitos-dia ocupados / leitos-dia disponíveis no período (ver view).
-- ----------------------------------------------------------------------------
SELECT
    nome_unidade,
    capacidade_leitos,
    leitos_dia_ocupados,
    ocupacao_estimada_pct,
    RANK() OVER (ORDER BY ocupacao_estimada_pct DESC) AS ranking
FROM vw_ocupacao_unidade
ORDER BY ranking;


-- ----------------------------------------------------------------------------
-- 7) Quais unidades estão acima da média do hospital em mais indicadores?
--    Compara permanência, espera e infecção de cada unidade com a média geral.
-- ----------------------------------------------------------------------------
WITH media_hospital AS (
    SELECT
        AVG(permanencia_dias)             AS permanencia,
        AVG(tempo_espera_min)             AS espera,
        100.0 * AVG(infeccao_hospitalar)  AS infeccao
    FROM vw_internacoes_detalhe
),
comparacao AS (
    SELECT
        i.nome_unidade,
        i.permanencia_media_dias > m.permanencia AS permanencia_acima,
        i.espera_media_min       > m.espera      AS espera_acima,
        i.taxa_infeccao_pct      > m.infeccao    AS infeccao_acima
    FROM vw_indicadores_unidade i
    CROSS JOIN media_hospital m
)
SELECT
    nome_unidade,
    permanencia_acima,
    espera_acima,
    infeccao_acima,
    permanencia_acima::int + espera_acima::int + infeccao_acima::int AS indicadores_acima_da_media
FROM comparacao
ORDER BY indicadores_acima_da_media DESC, nome_unidade;
