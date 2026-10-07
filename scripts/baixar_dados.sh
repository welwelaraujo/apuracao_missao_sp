#!/usr/bin/env bash
# Baixa os dados brutos do TSE/IBGE para a pasta tse/ (não versionada; ~1 GB).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p tse && cd tse
R=https://resultados.tse.jus.br/oficial/ele2026
O=https://cdn.tse.jus.br/estatistica/sead/odsele
curl -fsSO $O/votacao_secao/votacao_secao_2026_SP.zip
curl -fsSO $O/votacao_secao/votacao_secao_2026_BR.zip
curl -fsSO $O/eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip
curl -fsSO $R/6257/config/mun-e006257-cm.json
curl -fso sp-c0001.json $R/6257/dados/sp/sp-c0001-e006257-u.json
for c in 0006 0007; do curl -fso sp-c$c.json $R/6259/dados/sp/sp-c$c-e006259-u.json; done
curl -fso sp_mun.geojson "https://servicodados.ibge.gov.br/api/v3/malhas/estados/35?formato=application/vnd.geo%2Bjson&qualidade=minima&intrarregiao=municipio"
curl -fsO https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css
echo "ok"
