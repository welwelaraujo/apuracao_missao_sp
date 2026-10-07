"""Votos para Presidente (eleição 6257) nas seções de SP: votos válidos e votos de Renan Santos (14).

Incorpora o cargo '1' em tse/agg.pkl (gerado por agg.py), para que build_missao.py e secoes.py o tratem
como os demais cargos. Rodar depois de agg.py.
"""
import zipfile, os, pickle, time
import pandas as pd

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tse')
cols = ['SG_UF', 'CD_MUNICIPIO', 'NM_MUNICIPIO', 'NR_ZONA', 'NR_SECAO', 'CD_CARGO', 'NR_VOTAVEL', 'NM_VOTAVEL',
        'QT_VOTOS', 'NR_LOCAL_VOTACAO', 'NM_LOCAL_VOTACAO', 'DS_LOCAL_VOTACAO_ENDERECO']
t = time.time(); parts = []
with zipfile.ZipFile(os.path.join(D, 'votacao_secao_2026_BR.zip')).open('votacao_secao_2026_BR.csv') as f:
    for ch in pd.read_csv(f, sep=';', encoding='latin-1', usecols=cols, dtype=str, chunksize=3_000_000):
        ch = ch[(ch.SG_UF == 'SP') & (ch.CD_CARGO == '1')]
        parts.append(ch)
        print(round(time.time() - t), len(ch), flush=True)
P = pd.concat(parts)
P['QT_VOTOS'] = P.QT_VOTOS.astype(int)
P = P[~P.NR_VOTAVEL.isin(['95', '96', '97', '98'])]
P.to_pickle(os.path.join(D, 'presidente_sp.pkl'))   # nível seção, usado por secoes.py

A = pickle.load(open(os.path.join(D, 'agg.pkl'), 'rb'))
for k in [k for k in A['valid'] if k[3] == '1']: del A['valid'][k]
for k in [k for k in A['missao'] if k[3] == '1']: del A['missao'][k]
g = P.groupby(['CD_MUNICIPIO', 'NR_ZONA', 'NR_LOCAL_VOTACAO']).QT_VOTOS.sum()
for (m, z, l), v in g.items():
    A['valid'][(m, z, l, '1')] += int(v)
r = P[P.NR_VOTAVEL == '14']
for (m, z, l, mn, ln, le), v in r.groupby(['CD_MUNICIPIO', 'NR_ZONA', 'NR_LOCAL_VOTACAO', 'NM_MUNICIPIO', 'NM_LOCAL_VOTACAO',
                                          'DS_LOCAL_VOTACAO_ENDERECO']).QT_VOTOS.sum().items():
    A['missao'][(m, z, l, '1', '14')] += int(v)
    A['locinfo'].setdefault((m, z, l), (mn, ln, le))
A['names'][('1', '14')] = r.NM_VOTAVEL.iloc[0]
A['cargos']['1'] = 'Presidente'
pickle.dump(A, open(os.path.join(D, 'agg.pkl'), 'wb'))
novos = {k[:3] for k in A['valid'] if k[3] == '1'} - {k[:3] for k in A['valid'] if k[3] == '6'}
print('Renan Santos:', int(r.QT_VOTOS.sum()), '| válidos SP:', int(P.QT_VOTOS.sum()), '| locais só na presidencial:', len(novos))
