# Projeto 2 — Análise de indicadores hospitalares com SQL

Banco de dados em **PostgreSQL** com tabelas, views e consultas que respondem perguntas de
negócio de um hospital: tempo de internação, infecções, espera por atendimento, evolução
mensal e ocupação.

> Os dados são fictícios e foram gerados por `../scripts/gerar_dados.py`.

## Perguntas de negócio

1. Quais unidades têm maior tempo médio de internação?
2. Onde estão as infecções hospitalares e quanto tempo a mais os infectados ficam internados?
3. Quem espera mais para ser atendido?
4. Como evoluem as internações mês a mês?
5. Como a faixa etária se relaciona com permanência e óbitos?
6. Qual a ocupação estimada de cada unidade?
7. Quais unidades estão acima da média do hospital em mais indicadores?

## Estrutura

| Arquivo | O que faz |
|---|---|
| `01_criar_tabelas.sql` | Cria as tabelas com chaves primárias, chaves estrangeiras e regras de validação (`CHECK`) |
| `02_carregar_dados.sql` | Carrega os CSVs da pasta `dados/` e confere as contagens |
| `03_views.sql` | Cria 4 views reutilizáveis (detalhe das internações, indicadores por unidade, por mês e ocupação) |
| `04_consultas.sql` | As 7 consultas que respondem às perguntas acima |
| `resultados_consultas.txt` | Saída real das consultas, para consulta rápida sem precisar rodar |

### Modelo de dados

```
unidades (id_unidade) ──< leitos (id_leito)
      │                        │
      └──────< internacoes >───┘
```

- `unidades`: 8 unidades e a capacidade de leitos de cada uma
- `leitos`: 185 leitos, cada um pertence a uma unidade
- `internacoes`: 5.000 internações, ligadas a uma unidade e a um leito

## Como executar

Pré-requisito: PostgreSQL instalado e o comando `psql` disponível no terminal (no Windows,
adicione `C:\Program Files\PostgreSQL\<versão>\bin` ao PATH, ou use o "SQL Shell (psql)").

Execute **a partir da pasta raiz do repositório**, porque a carga lê os arquivos em `dados/`:

```powershell
psql -U postgres -c "CREATE DATABASE hospital;"
psql -U postgres -d hospital -f 02-sql-analise/01_criar_tabelas.sql
psql -U postgres -d hospital -f 02-sql-analise/02_carregar_dados.sql
psql -U postgres -d hospital -f 02-sql-analise/03_views.sql
psql -U postgres -d hospital -f 02-sql-analise/04_consultas.sql
```

Os scripts podem ser executados mais de uma vez: o primeiro recria as tabelas do zero. Avisos
`NOTICE` sobre `drop cascades` são normais. Testado no PostgreSQL 16.

## Resultados

**1. Maior tempo médio de internação** — a UTI Neonatal fica 8,1 dias acima da média do hospital (4,1 dias).

| Unidade | Internações | Permanência média (dias) | Diferença p/ média |
|---|---|---|---|
| UTI Neonatal | 171 | 12,2 | +8,1 |
| UTI Adulto | 303 | 8,7 | +4,6 |
| Clínica Médica | 948 | 5,6 | +1,5 |
| Ortopedia | 400 | 4,8 | +0,7 |
| Clínica Cirúrgica | 804 | 4,0 | −0,1 |
| Pediatria | 569 | 3,5 | −0,6 |
| Maternidade | 699 | 2,6 | −1,5 |
| Pronto-Socorro | 1.106 | 1,5 | −2,6 |

**2. Infecções** — as UTIs lideram (9,9% na Neonatal e 8,9% na Adulto). Em todas as unidades,
quem teve infecção ficou mais tempo internado; na UTI Adulto, 12,1 dias contra 8,4 dias.
É uma associação, não prova que a infecção causa a permanência maior (e o contrário também
é possível: quem fica mais tempo tem mais chance de se infectar).

**3. Espera por atendimento** — o Pronto-Socorro espera em média 120 min, com percentil 90 de
179 min, e 89,6% dos atendimentos passam de 60 min. Na ponta oposta, as UTIs praticamente
não têm espera.

| Unidade | Espera média (min) | Percentil 90 (min) | Acima de 60 min |
|---|---|---|---|
| Pronto-Socorro | 120 | 179 | 89,6% |
| Ortopedia | 89 | 137 | 79,5% |
| Clínica Cirúrgica | 70 | 105 | 63,6% |
| Clínica Médica | 60 | 92 | 48,0% |

**4. Evolução mensal** — o volume fica estável, entre 251 e 307 internações por mês, sem
tendência clara. A variação contra o mês anterior oscila entre −15,3% e +22,3%.

**5. Faixa etária** — a faixa de 0 a 11 anos tem a maior taxa de óbito (7,1%), contra algo
entre 2,8% e 3,7% nas demais. Isso reflete em boa parte a UTI Neonatal: a faixa etária está
misturada com o tipo de unidade.

**6. Ocupação estimada** — de 13,5% (Maternidade) a 38,3% (UTI Neonatal). É uma estimativa
(leitos-dia ocupados dividido pelos disponíveis no período) e os dados fictícios não foram
calibrados para reproduzir a ocupação de um hospital real, então vale mais para comparar
unidades entre si do que como valor absoluto.

**7. Unidades acima da média em mais indicadores** — a Ortopedia está acima da média do hospital
nos três (permanência, espera e infecção). Clínica Cirúrgica, Clínica Médica, UTI Adulto e UTI
Neonatal estão acima em dois. Maternidade e Pediatria não estão acima em nenhum.

A saída completa de todas as consultas está em [`resultados_consultas.txt`](resultados_consultas.txt).

## Técnicas demonstradas

Modelagem relacional com chaves e restrições, carga de dados com `\copy`, `JOIN`, `GROUP BY`,
agregações condicionais com `FILTER`, CTEs (`WITH`), funções de janela (`RANK`, `LAG`),
`PERCENTILE_CONT`, `CASE`, views reutilizáveis e scripts que podem ser reexecutados.

## Conferência

Os indicadores por unidade (permanência, espera e infecção) são os mesmos que o
[Projeto 1](../01-python-limpeza/) calcula em Python depois da limpeza, o que confirma que os
dois caminhos chegam ao mesmo resultado.

## Próximo passo

O [Projeto 3](../03-powerbi-dashboard/) leva essas views para um dashboard no Power BI.
