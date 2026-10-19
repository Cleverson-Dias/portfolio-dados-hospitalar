"""
Projeto 1 - Limpeza de dados e relatorio automatizado (Python + pandas)

Le dados/internacoes_brutas.csv (base com problemas tipicos de dados reais),
corrige o que for possivel, e gera em saida/:

  internacoes_limpa.csv          base tratada, pronta para SQL e Power BI
  relatorio.md                   o que foi encontrado/corrigido + indicadores por unidade
  permanencia_por_unidade.png    grafico com a permanencia media por unidade

Uso (a partir da pasta 01-python-limpeza):
  python limpar_dados.py
"""

from pathlib import Path

import pandas as pd

PASTA_PROJETO = Path(__file__).resolve().parent
RAIZ = PASTA_PROJETO.parent
ARQ_BRUTO = RAIZ / "dados" / "internacoes_brutas.csv"
ARQ_UNIDADES = RAIZ / "dados" / "unidades.csv"
PASTA_SAIDA = PASTA_PROJETO / "saida"

IDADE_MINIMA, IDADE_MAXIMA = 0, 110
HORA_PADRAO_SEM_HORA = 12  # data sem horario recebe 12:00 (premissa documentada no README)

# formatos de data encontrados na base bruta: (formato, tem_horario)
FORMATOS_DATA = [
    ("%Y-%m-%d %H:%M", True),
    ("%d/%m/%Y %H:%M", True),
    ("%d/%m/%Y", False),
]

NAO_INFORMADO = "Não informado"
CONVENIO_AUSENTE = {"n/i", "nao informado", "não informado"}
SEXO_PADRAO = {"F": "F", "FEMININO": "F", "M": "M", "MASCULINO": "M"}


# --------------------------------------------------------------------------- #
# Funcoes auxiliares
# --------------------------------------------------------------------------- #
def chave_texto(valor):
    """Normaliza texto para comparacao: sem espacos extras e sem diferenca de caixa."""
    return " ".join(str(valor).split()).casefold()


def converter_datas(serie):
    """Converte datas escritas em formatos diferentes.

    Retorna (datas, quantidade_sem_horario). Datas sem horario recebem 12:00.
    """
    formato, _ = FORMATOS_DATA[0]
    datas = pd.to_datetime(serie, format=formato, errors="coerce")
    sem_horario = 0

    for formato, tem_horario in FORMATOS_DATA[1:]:
        convertidas = pd.to_datetime(serie, format=formato, errors="coerce")
        novas = convertidas.notna() & datas.isna()
        if not tem_horario:
            convertidas = convertidas + pd.Timedelta(hours=HORA_PADRAO_SEM_HORA)
            sem_horario += int(novas.sum())
        datas = datas.fillna(convertidas)

    return datas, sem_horario


# --------------------------------------------------------------------------- #
# Limpeza
# --------------------------------------------------------------------------- #
def limpar(bruto, unidades):
    """Aplica todas as regras de limpeza. Retorna (base_limpa, registro_do_que_foi_feito)."""
    df = bruto.copy()
    log = {"linhas_lidas": len(df)}

    # 1) Texto: remove espacos nas pontas e transforma vazio em ausente
    for coluna in df.columns:
        df[coluna] = df[coluna].str.strip().replace("", pd.NA)

    # 2) Duplicatas
    antes = len(df)
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="id_internacao")
    log["duplicatas_removidas"] = antes - len(df)

    # 3) Unidade: padroniza o nome e recupera o id da unidade
    mapa = {chave_texto(nome): (i, nome) for i, nome in zip(unidades["id_unidade"], unidades["nome_unidade"])}
    chaves = df["unidade"].fillna("").map(chave_texto)
    df["id_unidade"] = chaves.map(lambda k: mapa.get(k, (pd.NA, pd.NA))[0])
    df["nome_unidade"] = chaves.map(lambda k: mapa.get(k, (pd.NA, pd.NA))[1])
    log["unidades_padronizadas"] = int((df["unidade"] != df["nome_unidade"]).sum())
    log["unidades_nao_reconhecidas"] = int(df["nome_unidade"].isna().sum())

    # 4) Datas: formatos misturados -> um formato unico
    df["data_entrada"], sem_hora_entrada = converter_datas(df["data_entrada"])
    df["data_saida"], sem_hora_saida = converter_datas(df["data_saida"])
    log["datas_sem_horario"] = sem_hora_entrada + sem_hora_saida
    log["saida_ausente"] = int(df["data_saida"].isna().sum())

    # 5) Permanencia em dias; saida antes da entrada e inconsistencia
    permanencia = (df["data_saida"] - df["data_entrada"]).dt.total_seconds() / 86400
    df["data_inconsistente"] = permanencia < 0
    log["saida_antes_da_entrada"] = int(df["data_inconsistente"].sum())
    df["permanencia_dias"] = permanencia.mask(df["data_inconsistente"]).round(2)

    # 6) Tempo de espera: negativo e impossivel
    df["tempo_espera_min"] = pd.to_numeric(df["tempo_espera_min"], errors="coerce")
    espera_invalida = df["tempo_espera_min"] < 0
    log["espera_negativa"] = int(espera_invalida.sum())
    df["tempo_espera_min"] = df["tempo_espera_min"].mask(espera_invalida)
    log["espera_ausente"] = int(df["tempo_espera_min"].isna().sum())

    # 7) Idade: fora de uma faixa plausivel
    df["idade"] = pd.to_numeric(df["idade"], errors="coerce")
    idade_invalida = (df["idade"] < IDADE_MINIMA) | (df["idade"] > IDADE_MAXIMA)
    log["idade_impossivel"] = int(idade_invalida.sum())
    df["idade"] = df["idade"].mask(idade_invalida)
    log["idade_ausente"] = int(df["idade"].isna().sum())

    # 8) Sexo: Feminino/Masculino -> F/M
    df["sexo"] = df["sexo"].str.upper().map(SEXO_PADRAO)
    log["sexo_padronizado"] = int((bruto.loc[df.index, "sexo"].str.strip() != df["sexo"]).sum())

    # 9) Convenio: varias formas de "nao informado" -> uma so
    convenio_ausente = df["convenio"].isna() | df["convenio"].str.casefold().isin(CONVENIO_AUSENTE)
    log["convenio_nao_informado"] = int(convenio_ausente.sum())
    df["convenio"] = df["convenio"].mask(convenio_ausente, NAO_INFORMADO)

    # 10) Tipos e ordem das colunas
    for coluna in ["id_internacao", "id_paciente", "id_unidade", "id_leito", "infeccao_hospitalar"]:
        df[coluna] = pd.to_numeric(df[coluna]).astype("Int64")

    colunas = [
        "id_internacao", "id_paciente", "id_unidade", "nome_unidade", "id_leito",
        "data_entrada", "data_saida", "permanencia_dias", "tempo_espera_min",
        "idade", "sexo", "convenio", "infeccao_hospitalar", "desfecho", "data_inconsistente",
    ]
    df = df[colunas].sort_values("id_internacao").reset_index(drop=True)
    log["linhas_finais"] = len(df)
    return df, log


# --------------------------------------------------------------------------- #
# Indicadores, relatorio e grafico
# --------------------------------------------------------------------------- #
def calcular_indicadores(df):
    base = df.assign(
        infeccao=df["infeccao_hospitalar"].astype(float),
        obito=(df["desfecho"] == "Óbito").astype(float),
    )
    indicadores = base.groupby("nome_unidade").agg(
        internacoes=("id_internacao", "count"),
        permanencia_media_dias=("permanencia_dias", "mean"),
        espera_media_min=("tempo_espera_min", "mean"),
        taxa_infeccao_pct=("infeccao", "mean"),
        taxa_obito_pct=("obito", "mean"),
    )
    indicadores["taxa_infeccao_pct"] *= 100
    indicadores["taxa_obito_pct"] *= 100
    return indicadores.sort_values("permanencia_media_dias", ascending=False).round(1)


def tabela_markdown(df, formatos=None):
    formatos = formatos or {}
    cabecalho = "| " + " | ".join(df.columns) + " |"
    separador = "|" + "|".join(["---"] * len(df.columns)) + "|"
    linhas = []
    for _, linha in df.iterrows():
        celulas = [formatos.get(c, str)(linha[c]) for c in df.columns]
        linhas.append("| " + " | ".join(celulas) + " |")
    return "\n".join([cabecalho, separador, *linhas])


def gerar_relatorio(df, log, indicadores):
    problemas = pd.DataFrame(
        [
            ("Linhas duplicadas", "Removidas", log["duplicatas_removidas"]),
            ("Nome da unidade digitado de formas diferentes", "Padronizado pelo cadastro de unidades", log["unidades_padronizadas"]),
            ("Datas sem horário", "Assumido 12:00", log["datas_sem_horario"]),
            ("Data de saída ausente", "Mantida vazia (internação sem permanência calculável)", log["saida_ausente"]),
            ("Saída antes da entrada", "Permanência anulada e linha sinalizada em data_inconsistente", log["saida_antes_da_entrada"]),
            ("Tempo de espera negativo", "Convertido em ausente", log["espera_negativa"]),
            ("Tempo de espera ausente (total após limpeza)", "Mantido vazio, fora das médias", log["espera_ausente"]),
            ("Idade impossível (fora de 0-110)", "Convertida em ausente", log["idade_impossivel"]),
            ("Idade ausente (total após limpeza)", "Mantida vazia", log["idade_ausente"]),
            ("Sexo escrito por extenso", "Padronizado em F/M", log["sexo_padronizado"]),
            ("Convênio ausente ou 'N/I'", f"Padronizado como '{NAO_INFORMADO}'", log["convenio_nao_informado"]),
        ],
        columns=["problema", "tratamento", "linhas_afetadas"],
    )

    tabela_indicadores = indicadores.reset_index().rename(columns={
        "nome_unidade": "unidade",
        "internacoes": "internações",
        "permanencia_media_dias": "permanência média (dias)",
        "espera_media_min": "espera média (min)",
        "taxa_infeccao_pct": "infecção (%)",
        "taxa_obito_pct": "óbito (%)",
    })

    periodo_inicio = df["data_entrada"].min().strftime("%d/%m/%Y")
    periodo_fim = df["data_entrada"].max().strftime("%d/%m/%Y")

    return f"""# Relatório de limpeza e indicadores

Dados **fictícios**. Gerado automaticamente por `limpar_dados.py`.

## Resumo

- Linhas lidas: **{log['linhas_lidas']}**
- Linhas após a limpeza: **{log['linhas_finais']}**
- Período das internações: {periodo_inicio} a {periodo_fim}

## O que foi encontrado e como foi tratado

{tabela_markdown(problemas)}

## Indicadores por unidade (ordenado por permanência média)

{tabela_markdown(tabela_indicadores)}

As médias de permanência e espera ignoram os valores ausentes ou inválidos.
"""


def gerar_grafico(indicadores, caminho):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib não instalado: gráfico não gerado (pip install matplotlib).")
        return

    dados = indicadores["permanencia_media_dias"].sort_values()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    barras = ax.barh(dados.index, dados.values, color="#2a6f97")
    ax.bar_label(barras, labels=[f"{v:.1f}" for v in dados.values], padding=4)
    ax.set_xlabel("Permanência média (dias)")
    ax.set_title("Permanência média por unidade (dados fictícios)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, dados.max() * 1.12)
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)


# --------------------------------------------------------------------------- #
def main():
    PASTA_SAIDA.mkdir(exist_ok=True)

    bruto = pd.read_csv(ARQ_BRUTO, dtype=str, keep_default_na=False)
    unidades = pd.read_csv(ARQ_UNIDADES)

    limpa, log = limpar(bruto, unidades)
    indicadores = calcular_indicadores(limpa)

    limpa.to_csv(PASTA_SAIDA / "internacoes_limpa.csv", index=False, date_format="%Y-%m-%d %H:%M")
    (PASTA_SAIDA / "relatorio.md").write_text(gerar_relatorio(limpa, log, indicadores), encoding="utf-8")
    gerar_grafico(indicadores, PASTA_SAIDA / "permanencia_por_unidade.png")

    print(f"{log['linhas_lidas']} linhas lidas -> {log['linhas_finais']} linhas limpas")
    print(f"Arquivos gerados em: {PASTA_SAIDA}")


if __name__ == "__main__":
    main()
