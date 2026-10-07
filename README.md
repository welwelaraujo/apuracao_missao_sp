# Apuração da Missão em São Paulo – Eleições 2026

Mapa interativo dos votos do partido Missão (14) em cada local de votação (escola) do estado de São Paulo, 1º turno de 04/10/2026. Inclui Renan Santos (Presidente), filtrado apenas para os votos no estado de SP.

**Mapa:** https://welwelaraujo.github.io/apuracao_missao_sp/

## O que o mapa mostra

- **Distribuição**: mapa de calor dos votos da Missão para Presidente (Renan Santos, só votos em SP), Deputado Federal, Deputado Estadual e Senado, em votos absolutos ou em % dos votos válidos de cada escola. Dá para ver o partido inteiro ou um candidato. Ao lado aparecem os municípios e as escolas com mais votos. A partir do zoom 11, cada escola vira um círculo clicável.
- **Comparar candidatos**: sobrepõe dois candidatos para procurar possíveis dobradinhas. O mapa destaca as escolas onde os dois foram fortes ao mesmo tempo. A aba mostra também:
  - a correlação entre os % de cada um por escola;
  - um índice de sobreposição geográfica;
  - um gráfico de dispersão.

  Para cada candidato da Missão com pelo menos 1.000 votos, o mapa sugere os candidatos do outro cargo, de qualquer partido, com votação mais parecida.

- **Microdados**: o botão "Baixar CSV por seção" baixa os votos do filtro atual (cargo e candidato, ou a Missão inteira) por seção eleitoral. Cada linha traz município, zona, seção, local de votação, endereço, bairro, candidato, votos e votos válidos da seção. O CSV usa `;` como separador e abre direto no Excel. O download só funciona na versão publicada (GitHub Pages), não abrindo o arquivo localmente.

Correlação alta é um indício geográfico, não prova. O voto é secreto, então não dá para afirmar que foram os mesmos eleitores.

## Arquivos

| Caminho | Conteúdo |
|---|---|
| `index.html` | O mapa, com os dados embutidos. É a página publicada no GitHub Pages. |
| `dados/votacao_missao_sp_2026.xlsx` | Planilha com as abas Resumo, Por município, Por local de votação e Possíveis dobradinhas. |
| `dados/missao_data.json` | Dados usados pelo mapa: locais, votos por candidato e parceiros sugeridos. |
| `dados/secoes_c1.txt`, `secoes_c5.txt`, `secoes_c6.txt`, `secoes_c7.txt` | Votos da Missão por seção (Presidente, Senado, Dep. Federal, Dep. Estadual), usados pelo botão de microdados. |
| `dados/enderecos.json` | Endereço de cada local de votação. |
| `dados/sp_mun_small.geojson` | Contornos dos municípios de SP (IBGE, simplificado). |
| `scripts/` | Pipeline de processamento. |

## Como reproduzir

Requer Python 3 com `pandas`, `numpy` e `openpyxl`.

```bash
bash scripts/baixar_dados.sh      # baixa ~1,1 GB de dados brutos do TSE/IBGE para tse/
python scripts/locais.py          # coordenadas e eleitorado de cada local de votação
python scripts/agg.py             # votos da Missão e votos válidos por local (~2 min)
python scripts/agg2.py            # votos de todos os candidatos a deputado por local
python scripts/presidente.py      # votos para Presidente nas seções de SP (arquivo nacional filtrado)
python scripts/build_missao.py    # análise de dobradinhas, dados do mapa e planilha
python scripts/secoes.py          # microdados por seção para o download
python scripts/build_html.py      # gera o index.html
```

## Fontes

- TSE, dados abertos: [votação por seção eleitoral SP 2026](https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2026_SP.zip), [votação por seção eleitoral BR 2026](https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2026_BR.zip) (Presidente, filtrado para SP) e [eleitorado por local de votação 2026](https://cdn.tse.jus.br/estatistica/sead/odsele/eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip).
- TSE, [resultados oficiais](https://resultados.tse.jus.br/oficial/app/index.html#/eleicao/6257/uf/sp), usados para situação dos candidatos, partidos e conferência dos totais.
- IBGE, malha municipal de SP.
- Mapa de fundo: Esri World Street Map e Light Gray Canvas.

## Observações

- Os totais por candidato, somados a partir das seções, conferem exatamente com o resultado oficial do TSE.
- Os "votos válidos" de cada local incluem os votos de candidatos com registro anulado sub judice, cerca de 0,16% do total. Por isso as porcentagens podem diferir levemente das oficiais.
- 51 locais sem coordenadas no cadastro do TSE aparecem no centro do respectivo município.
