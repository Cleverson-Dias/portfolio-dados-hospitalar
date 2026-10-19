# Relatório de limpeza e indicadores

Dados **fictícios**. Gerado automaticamente por `limpar_dados.py`.

## Resumo

- Linhas lidas: **5100**
- Linhas após a limpeza: **5000**
- Período das internações: 01/01/2025 a 30/06/2026

## O que foi encontrado e como foi tratado

| problema | tratamento | linhas_afetadas |
|---|---|---|
| Linhas duplicadas | Removidas | 100 |
| Nome da unidade digitado de formas diferentes | Padronizado pelo cadastro de unidades | 1775 |
| Datas sem horário | Assumido 12:00 | 2474 |
| Data de saída ausente | Mantida vazia (internação sem permanência calculável) | 96 |
| Saída antes da entrada | Permanência anulada e linha sinalizada em data_inconsistente | 12 |
| Tempo de espera negativo | Convertido em ausente | 28 |
| Tempo de espera ausente (total após limpeza) | Mantido vazio, fora das médias | 223 |
| Idade impossível (fora de 0-110) | Convertida em ausente | 15 |
| Idade ausente (total após limpeza) | Mantida vazia | 155 |
| Sexo escrito por extenso | Padronizado em F/M | 1690 |
| Convênio ausente ou 'N/I' | Padronizado como 'Não informado' | 161 |

## Indicadores por unidade (ordenado por permanência média)

| unidade | internações | permanência média (dias) | espera média (min) | infecção (%) | óbito (%) |
|---|---|---|---|---|---|
| UTI Neonatal | 171 | 12.2 | 14.1 | 9.9 | 18.7 |
| UTI Adulto | 303 | 8.7 | 25.1 | 8.9 | 14.2 |
| Clínica Médica | 948 | 5.6 | 60.1 | 4.1 | 1.5 |
| Ortopedia | 400 | 4.8 | 89.1 | 3.8 | 2.8 |
| Clínica Cirúrgica | 804 | 4.0 | 69.5 | 4.5 | 1.7 |
| Pediatria | 569 | 3.5 | 44.8 | 2.3 | 4.0 |
| Maternidade | 699 | 2.6 | 29.5 | 2.1 | 2.3 |
| Pronto-Socorro | 1106 | 1.5 | 119.3 | 1.4 | 2.7 |

As médias de permanência e espera ignoram os valores ausentes ou inválidos.
