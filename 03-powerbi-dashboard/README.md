# Dashboard de indicadores hospitalares

Painel web em HTML, CSS e JavaScript que lê os CSVs gerados pelo projeto.
A base é simulada e não contém prontuários reais.

## Como abrir

Na raiz do repositório, execute:

```sh
python -m http.server 8000
```

Abra [http://localhost:8000/03-powerbi-dashboard/](http://localhost:8000/03-powerbi-dashboard/).
Não é necessário instalar dependências. O servidor permite que o navegador leia os arquivos da pasta `dados/`.

## Como explorar

- Selecione as datas inicial e final e a unidade para recalcular os cartões, o gráfico e a tabela.
- Alterne o indicador no gráfico mensal para comparar internações, ocupação, permanência, espera ou infecção.
- Use a tabela para comparar as oito unidades. O total de leitos vem de `dados/unidades.csv`.

## Métricas

| Indicador | Cálculo |
| --- | --- |
| Internações | Registros cuja data de entrada está no intervalo selecionado, incluindo as duas datas. |
| Permanência média | Média do tempo completo entre entrada e saída das internações iniciadas no período, em dias. |
| Espera média | Média dos minutos de espera das internações iniciadas no período. |
| Taxa de infecção | Internações com infecção divididas pelas internações iniciadas no período. |
| Ocupação de leitos | Soma do tempo ocupado por leito, dividida pelo tempo disponível de todos os leitos da unidade ou das unidades selecionadas. |

A ocupação considera internações em andamento durante o período, mesmo quando a entrada foi anterior.
Cada intervalo é recortado pelos limites do filtro. Quando a base simulada atribui duas internações
simultâneas ao mesmo leito, o painel conta o tempo compartilhado uma vez. Por essa razão, o resultado
pode diferir da estimativa da view SQL `vw_ocupacao_unidade`, que soma a permanência completa
das internações. No gráfico, cada mês usa somente a parte incluída no filtro.
