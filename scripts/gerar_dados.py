"""
Gera o dataset hospitalar FICTÍCIO usado nos três projetos do portfólio.

Saídas (pasta dados/):
  unidades.csv            -> cadastro das unidades hospitalares
  leitos.csv              -> leitos de cada unidade
  internacoes.csv         -> base consistente (usada no SQL e no Power BI)
  internacoes_brutas.csv  -> mesma base com "sujeira" proposital
                             (usada no projeto de limpeza em Python)

Todos os dados são inventados. Use a mesma SEED para obter sempre o mesmo resultado.

Uso:
  python scripts/gerar_dados.py
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 42
N_INTERNACOES = 5000
INICIO = datetime(2025, 1, 1)
FIM = datetime(2026, 6, 30)

PASTA_DADOS = Path(__file__).resolve().parent.parent / "dados"

# nome, capacidade de leitos, média de dias de internação, espera média (min),
# probabilidade de infecção hospitalar, peso (volume relativo de internações)
UNIDADES = [
    ("UTI Adulto",          20, 9.0, 25, 0.12, 6),
    ("UTI Neonatal",        10, 12.0, 15, 0.09, 3),
    ("Clínica Médica",      40, 5.5, 60, 0.04, 20),
    ("Clínica Cirúrgica",   30, 4.0, 70, 0.05, 15),
    ("Ortopedia",           20, 4.5, 90, 0.03, 8),
    ("Pediatria",           25, 3.5, 45, 0.02, 12),
    ("Maternidade",         25, 2.5, 30, 0.015, 14),
    ("Pronto-Socorro",      15, 1.5, 120, 0.01, 22),
]

CONVENIOS = ["SUS", "Particular", "Convênio A", "Convênio B", "Convênio C"]
PESO_CONVENIOS = [55, 10, 15, 12, 8]


def gerar_unidades_e_leitos():
    unidades, leitos = [], []
    id_leito = 1
    for i, (nome, cap, *_resto) in enumerate(UNIDADES, start=1):
        unidades.append({"id_unidade": i, "nome_unidade": nome, "capacidade_leitos": cap})
        for n in range(1, cap + 1):
            leitos.append({
                "id_leito": id_leito,
                "id_unidade": i,
                "numero_leito": f"{nome[:3].upper()}-{n:02d}",
            })
            id_leito += 1
    return unidades, leitos


def gerar_internacoes(leitos):
    leitos_por_unidade = {}
    for l in leitos:
        leitos_por_unidade.setdefault(l["id_unidade"], []).append(l["id_leito"])

    pesos = [u[5] for u in UNIDADES]
    total_dias = (FIM - INICIO).days
    linhas = []

    for i in range(1, N_INTERNACOES + 1):
        idx = random.choices(range(len(UNIDADES)), weights=pesos)[0]
        nome, _cap, media_dias, espera_media, p_infeccao, _peso = UNIDADES[idx]
        id_unidade = idx + 1

        entrada = INICIO + timedelta(
            days=random.randint(0, total_dias),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        permanencia = max(0.2, random.gammavariate(2.0, media_dias / 2.0))
        saida = entrada + timedelta(days=permanencia)

        espera = max(0, int(random.gauss(espera_media, espera_media * 0.4)))

        idade = min(100, max(0, int(random.gauss(45, 22))))
        if nome in ("Pediatria", "UTI Neonatal"):
            idade = random.randint(0, 14) if nome == "Pediatria" else 0
        if nome == "Maternidade":
            idade = random.randint(16, 44)

        # infecção fica mais provável quanto maior a permanência
        p = min(0.9, p_infeccao * (0.6 + permanencia / media_dias * 0.4))
        infeccao = 1 if random.random() < p else 0

        sorteio = random.random()
        if nome.startswith("UTI") and sorteio < 0.14:
            desfecho = "Óbito"
        elif sorteio < 0.02:
            desfecho = "Óbito"
        elif sorteio < 0.09:
            desfecho = "Transferência"
        else:
            desfecho = "Alta"

        linhas.append({
            "id_internacao": i,
            "id_paciente": random.randint(10000, 19999),
            "id_unidade": id_unidade,
            "id_leito": random.choice(leitos_por_unidade[id_unidade]),
            "data_entrada": entrada.strftime("%Y-%m-%d %H:%M"),
            "data_saida": saida.strftime("%Y-%m-%d %H:%M"),
            "tempo_espera_min": espera,
            "idade": idade,
            "sexo": "F" if nome == "Maternidade" else random.choice(["F", "M"]),
            "convenio": random.choices(CONVENIOS, weights=PESO_CONVENIOS)[0],
            "infeccao_hospitalar": infeccao,
            "desfecho": desfecho,
        })
    return linhas


def sujar(linhas, unidades):
    """Cria uma versão 'bruta' com problemas típicos de dados reais."""
    nome_por_id = {u["id_unidade"]: u["nome_unidade"] for u in unidades}
    sujas = []

    for l in linhas:
        s = dict(l)
        # a base bruta traz o nome da unidade (digitado de formas diferentes)
        nome = nome_por_id[s.pop("id_unidade")]
        s["unidade"] = random.choice([
            nome, nome, nome, nome.upper(), nome.lower(), f" {nome} ", nome.replace(" ", "  "),
        ])

        # formatos de data misturados
        for campo in ("data_entrada", "data_saida"):
            dt = datetime.strptime(s[campo], "%Y-%m-%d %H:%M")
            s[campo] = random.choice([
                dt.strftime("%Y-%m-%d %H:%M"),
                dt.strftime("%Y-%m-%d %H:%M"),
                dt.strftime("%d/%m/%Y %H:%M"),
                dt.strftime("%d/%m/%Y"),
            ])

        # valores ausentes
        if random.random() < 0.04:
            s["tempo_espera_min"] = ""
        if random.random() < 0.03:
            s["idade"] = ""
        if random.random() < 0.02:
            s["data_saida"] = ""
        if random.random() < 0.03:
            s["convenio"] = random.choice(["", "N/I", "nao informado"])

        # valores impossíveis
        if random.random() < 0.01:
            s["tempo_espera_min"] = -random.randint(1, 60)
        if random.random() < 0.005:
            s["idade"] = random.choice([150, 999, -1])

        # sexo escrito de várias formas
        s["sexo"] = random.choice([s["sexo"], s["sexo"], {"F": "Feminino", "M": "Masculino"}[s["sexo"]]])

        sujas.append(s)

    # linhas duplicadas
    duplicadas = random.sample(sujas, k=int(len(sujas) * 0.02))
    sujas.extend(dict(d) for d in duplicadas)
    random.shuffle(sujas)
    return sujas


def salvar(nome_arquivo, linhas):
    caminho = PASTA_DADOS / nome_arquivo
    campos = list(linhas[0].keys())
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)
    print(f"{nome_arquivo}: {len(linhas)} linhas")


def main():
    random.seed(SEED)
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)

    unidades, leitos = gerar_unidades_e_leitos()
    internacoes = gerar_internacoes(leitos)
    brutas = sujar(internacoes, unidades)

    salvar("unidades.csv", unidades)
    salvar("leitos.csv", leitos)
    salvar("internacoes.csv", internacoes)
    salvar("internacoes_brutas.csv", brutas)


if __name__ == "__main__":
    main()
