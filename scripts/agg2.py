"""Matriz local de votação x votável (dep. federal e estadual, todos os partidos) para análise de dobradinhas."""
import zipfile, os, time, pickle
import numpy as np, pandas as pd

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tse')
z = zipfile.ZipFile(os.path.join(D, 'votacao_secao_2026_SP.zip'))
cols = ['CD_MUNICIPIO', 'NR_ZONA', 'CD_CARGO', 'NR_VOTAVEL', 'NM_VOTAVEL', 'QT_VOTOS', 'NR_LOCAL_VOTACAO']
t = time.time(); parts = []; names = {}
with z.open('votacao_secao_2026_SP.csv') as f:
    for i, ch in enumerate(pd.read_csv(f, sep=';', encoding='latin-1', usecols=cols, chunksize=3_000_000,
                                       dtype={'CD_MUNICIPIO': 'int32', 'NR_ZONA': 'int16', 'CD_CARGO': 'int8',
                                              'NR_VOTAVEL': 'int32', 'QT_VOTOS': 'int32', 'NR_LOCAL_VOTACAO': 'int32',
                                              'NM_VOTAVEL': 'string'})):
        ch = ch[ch.CD_CARGO.isin([6, 7]) & ~ch.NR_VOTAVEL.isin([95, 96, 97, 98])]
        nm = ch.drop_duplicates(['CD_CARGO', 'NR_VOTAVEL'])
        for c, n, s in zip(nm.CD_CARGO, nm.NR_VOTAVEL, nm.NM_VOTAVEL):
            names[(int(c), int(n))] = s
        parts.append(ch.groupby(['CD_MUNICIPIO', 'NR_ZONA', 'NR_LOCAL_VOTACAO', 'CD_CARGO', 'NR_VOTAVEL'], observed=True)
                     .QT_VOTOS.sum().reset_index())
        print(i, round(time.time() - t), flush=True)
g = pd.concat(parts).groupby(['CD_MUNICIPIO', 'NR_ZONA', 'NR_LOCAL_VOTACAO', 'CD_CARGO', 'NR_VOTAVEL']).QT_VOTOS.sum().reset_index()
g.to_parquet(os.path.join(D, 'loc_votavel.parquet')) if False else g.to_pickle(os.path.join(D, 'loc_votavel.pkl'))
pickle.dump(names, open(os.path.join(D, 'votavel_names.pkl'), 'wb'))
print('done', len(g), round(time.time() - t))
