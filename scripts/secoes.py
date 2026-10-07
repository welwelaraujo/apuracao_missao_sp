"""Microdados por seção: votos da Missão por seção eleitoral, para o botão de download do mapa.

Gera dados/secoes_c{cargo}.txt (uma linha por seção com voto na Missão) e dados/enderecos.json.
Formato da linha: indice_local,nr_secao,votos_validos_secao,cand:votos|cand:votos...
(indice_local e cand são posições nas listas locs e cands de dados/missao_data.json).
Rodar depois de build_missao.py.
"""
import zipfile, os, json, pickle, time
import pandas as pd

S = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(S, '..', 'tse'); OUTD = os.path.join(S, '..', 'dados')
A = pickle.load(open(os.path.join(D, 'agg.pkl'), 'rb'))
LOC = pickle.load(open(os.path.join(D, 'locais.pkl'), 'rb'))
PD = json.load(open(os.path.join(OUTD, 'missao_data.json'), encoding='utf-8'))
locs = sorted({k[:3] for k in A['valid']})          # mesma ordem de pagedata.py
assert len(locs) == len(PD['locs'])
lix = {(int(m), int(z), int(l)): i for i, (m, z, l) in enumerate(locs)}
cix = {(int(c['c']), int(c['n'])): i for i, c in enumerate(PD['cands']) if c['m']}

cols = ['CD_MUNICIPIO', 'NR_ZONA', 'NR_SECAO', 'CD_CARGO', 'NR_VOTAVEL', 'QT_VOTOS', 'NR_LOCAL_VOTACAO']
dt = {'CD_MUNICIPIO': 'int32', 'NR_ZONA': 'int16', 'NR_SECAO': 'int16', 'CD_CARGO': 'int8', 'NR_VOTAVEL': 'int32',
      'QT_VOTOS': 'int32', 'NR_LOCAL_VOTACAO': 'int32'}
val, mis = [], []
t = time.time()
with zipfile.ZipFile(os.path.join(D, 'votacao_secao_2026_SP.zip')).open('votacao_secao_2026_SP.csv') as f:
    for ch in pd.read_csv(f, sep=';', encoding='latin-1', usecols=cols, dtype=dt, chunksize=3_000_000):
        ch = ch[ch.CD_CARGO.isin([5, 6, 7]) & ~ch.NR_VOTAVEL.isin([95, 96, 97, 98])]
        k = ['CD_MUNICIPIO', 'NR_ZONA', 'NR_LOCAL_VOTACAO', 'NR_SECAO', 'CD_CARGO']
        val.append(ch.groupby(k).QT_VOTOS.sum())
        m = ch[[(int(c), int(n)) in cix for c, n in zip(ch.CD_CARGO, ch.NR_VOTAVEL)]]
        mis.append(m)
        print(round(time.time() - t), flush=True)
val = pd.concat(val).groupby(level=list(range(5))).sum()
mis = pd.concat(mis).groupby(['CD_MUNICIPIO', 'NR_ZONA', 'NR_LOCAL_VOTACAO', 'NR_SECAO', 'CD_CARGO', 'NR_VOTAVEL']).QT_VOTOS.sum().reset_index()
mis = mis[mis.QT_VOTOS > 0]

for cargo in (5, 6, 7):
    mc = mis[mis.CD_CARGO == cargo]
    lines = []
    for (mu, z, l, s), g in mc.groupby(['CD_MUNICIPIO', 'NR_ZONA', 'NR_LOCAL_VOTACAO', 'NR_SECAO']):
        li = lix[(mu, z, l)]
        pairs = '|'.join(f'{cix[(cargo, int(n))]}:{int(q)}' for n, q in sorted(zip(g.NR_VOTAVEL, g.QT_VOTOS), key=lambda x: -x[1]))
        lines.append(f'{li},{s},{int(val.get((mu, z, l, s, cargo), 0))},{pairs}')
    p = os.path.join(OUTD, f'secoes_c{cargo}.txt')
    open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
    print(cargo, len(lines), 'seções', os.path.getsize(p) // 1024, 'KB', 'votos', int(mc.QT_VOTOS.sum()))

end = []
for k in locs:
    li = LOC.get(k)
    end.append(((li or {}).get('end') or A['locinfo'].get(k, ('', '', ''))[2] or '').strip())
json.dump(end, open(os.path.join(OUTD, 'enderecos.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('ok', round(time.time() - t))
