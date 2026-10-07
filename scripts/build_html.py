"""Monta o index.html (mapa) a partir do template e dos dados gerados por build_missao.py."""
import os

S = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(S, '..')
t = open(os.path.join(S, 'missao_template.html'), encoding='utf-8').read()
css = open(os.path.join(R, 'tse', 'leaflet.css'), encoding='utf-8').read()
data = open(os.path.join(R, 'dados', 'missao_data.json'), encoding='utf-8').read().replace('</', '<' + chr(92) + '/')
geo = open(os.path.join(R, 'dados', 'sp_mun_small.geojson'), encoding='utf-8').read()
t = t.replace('/*__LEAFLET_CSS__*/', css).replace('__DATA__', data).replace('__GEO__', geo)

# mapa de fundo (Esri): funciona tanto no GitHub Pages quanto abrindo o arquivo localmente
old = "const muni = L.geoJSON(GEO, {style:()=>({color:css('--mapline'), weight:.6, fillColor:css('--mapfill'), fillOpacity:1})"
assert old in t
E = 'https://server.arcgisonline.com/ArcGIS/rest/services/'
att = 'Tiles &copy; Esri &mdash; Esri, HERE, Garmin, OpenStreetMap contributors'
tiles = f"""const ruas = L.tileLayer('{E}World_Street_Map/MapServer/tile/{{z}}/{{y}}/{{x}}',{{maxZoom:19,attribution:'{att}'}}).addTo(map);
const cinza = L.layerGroup([L.tileLayer('{E}Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}',{{maxZoom:16,attribution:'{att}'}}),
  L.tileLayer('{E}Canvas/World_Light_Gray_Reference/MapServer/tile/{{z}}/{{y}}/{{x}}',{{maxZoom:16}})]);
L.control.layers({{'Ruas':ruas,'Cinza com nomes':cinza}},null,{{position:'topright',collapsed:false}}).addTo(map);
"""
t = t.replace(old, tiles + old.replace('fillOpacity:1', 'fillOpacity:0'))
t = ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
     + t.replace('<div class="wrap">', '</head><body><div class="wrap">', 1) + '</body></html>')
open(os.path.join(R, 'index.html'), 'w', encoding='utf-8').write(t)
print('index.html', len(t))
