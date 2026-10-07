"""Extrai coordenadas, nome, bairro e eleitorado de cada local de votação de SP (cadastro TSE 2026)."""
import zipfile, io, csv, pickle, collections, os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tse')
z = zipfile.ZipFile(os.path.join(D, 'eleitorado_local_votacao_2026.zip'))
f = io.TextIOWrapper(z.open('eleitorado_local_votacao_2026_SP.csv'), encoding='latin-1', newline='')
L = {}; el = collections.Counter(); bad = 0
for row in csv.DictReader(f, delimiter=';'):
    k = (row['CD_MUNICIPIO'], row['NR_ZONA'], row['NR_LOCAL_VOTACAO'])
    el[k] += int(row['QT_ELEITOR_ELEICAO_ESTADUAL'] or 0)
    if k not in L:
        try:
            lat = float(row['NR_LATITUDE'].replace(',', '.')); lon = float(row['NR_LONGITUDE'].replace(',', '.'))
        except ValueError:
            lat = lon = None
        if lat is None or not (-26 < lat < -19 and -54 < lon < -44):
            lat = lon = None; bad += 1
        L[k] = dict(mun=row['NM_MUNICIPIO'], nome=row['NM_LOCAL_VOTACAO'], end=row['DS_ENDERECO'], bairro=row['NM_BAIRRO'],
                    tipo=row['DS_TIPO_LOCAL'], lat=lat, lon=lon)
for k in L:
    L[k]['eleitores'] = el[k]
pickle.dump(L, open(os.path.join(D, 'locais.pkl'), 'wb'))
print(len(L), 'locais; sem coordenadas:', bad)
