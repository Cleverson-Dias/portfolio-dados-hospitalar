# Portfólio de Dados — Indicadores Hospitalares

Três projetos independentes que contam uma história de ponta a ponta sobre o mesmo
conjunto de dados **fictícios** de um hospital: do dado bruto até o dashboard.

> Todos os dados são gerados por script e não representam pacientes reais.

## Os projetos

| # | Projeto | Ferramentas | O que responde |
|---|---------|-------------|----------------|
| 1 | [Limpeza e relatório automatizado](01-python-limpeza/) | Python, pandas | Como transformar uma base suja em uma base confiável e gerar um relatório automaticamente? |
| 2 | [Análise com SQL](02-sql-analise/) | SQL | Quais unidades têm maior tempo médio de internação? Onde estão as infecções? Quem espera mais? |
| 3 | [Dashboard de indicadores](03-powerbi-dashboard/) | Power BI | Como acompanhar internações, ocupação de leitos, tempo de espera e infecções num só painel? |

## Fluxo dos dados

```
scripts/gerar_dados.py
        │
        ├── dados/internacoes_brutas.csv ──► 01-python-limpeza ──► base limpa + relatório
        │
        └── dados/*.csv (unidades, leitos, internacoes) ──► 02-sql-analise ──► 03-powerbi-dashboard
```

## Como reproduzir

1. Gere os dados: `python scripts/gerar_dados.py`
2. Os arquivos CSV aparecem em `dados/`.
3. Siga o README de cada projeto.

## Dicionário de dados

**unidades.csv** — `id_unidade`, `nome_unidade`, `capacidade_leitos`

**leitos.csv** — `id_leito`, `id_unidade`, `numero_leito`

**internacoes.csv**

| Coluna | Descrição |
|--------|-----------|
| `id_internacao` | Identificador da internação |
| `id_paciente` | Identificador fictício do paciente |
| `id_unidade` / `id_leito` | Onde o paciente ficou |
| `data_entrada` / `data_saida` | Datas e horas da internação |
| `tempo_espera_min` | Minutos de espera até o atendimento |
| `idade`, `sexo`, `convenio` | Perfil do paciente |
| `infeccao_hospitalar` | 1 = teve infecção, 0 = não |
| `desfecho` | Alta, Transferência ou Óbito |

**internacoes_brutas.csv** — mesma informação, com problemas propositais: datas em formatos
diferentes, valores ausentes, idades e esperas impossíveis, nomes de unidade digitados de
formas diferentes, sexo escrito de várias maneiras e linhas duplicadas.

## Sobre mim

Estudante de Big Data no FATEC, em busca de oportunidade na área de dados.
linkedin: https://www.linkedin.com/in/cleversonalvesdias 
Email: cleversonalvesdias@gmail.com