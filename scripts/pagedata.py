# executed inside build_missao.py: builds page data + dobradinha analysis
import numpy as np, pandas as pd

G = pd.read_pickle(os.path.join(D, 'loc_votavel.pkl'))
# party / urna name for every deputy candidate in SP
INFO = {}
for c in ('6', '7'):
    d = json.load(open(os.path.join(D, f'sp-c000{c}.json'), encoding='utf-8'))
    for a in d['carg'][0]['agr']:
        for p in a['par']:
            for x in p['cand']:
                INFO[(c, x['n'])] = dict(nm=x['nmu'], par=p['sg'], st=x['st'], v=int(x['vap']))
            INFO[(c, p['n'])] = dict(nm=f"Legenda {p['sg']}", par=p['sg'], st='Legenda', v=int(p['tvtl']))

locs = sorted({k[:3] for k in valid})
lix = {k: i for i, k in enumerate(locs)}
NLc = len(locs)
muns = sorted({(LOC.get(k) or {}).get('mun') or A['locinfo'].get(k, ('?',))[0] for k in locs})
midx = {m: i for i, m in enumerate(muns)}
W = {c: np.zeros(NLc) for c in ('6', '7', '5', '1')}
for k, v in valid.items():
    if k[3] in W: W[k[3]][lix[k[:3]]] += v

# dense matrices per cargo (deputies, all parties)
G['li'] = [lix[(str(m), str(z), str(l))] for m, z, l in zip(G.CD_MUNICIPIO, G.NR_ZONA, G.NR_LOCAL_VOTACAO)]
MAT, COLS = {}, {}
for c in ('6', '7'):
    gc = G[G.CD_CARGO == int(c)]
    nums = sorted(gc.NR_VOTAVEL.unique())
    ci = {n: i for i, n in enumerate(nums)}
    M = np.zeros((NLc, len(nums)), dtype=np.float32)
    np.add.at(M, (gc.li.values, gc.NR_VOTAVEL.map(ci).values), gc.QT_VOTOS.values)
    MAT[c], COLS[c] = M, [str(n) for n in nums]
# Missão: Senado (144) e Presidente (14) a partir de agg.pkl
MV = {('5', '144'): np.zeros(NLc), ('1', '14'): np.zeros(NLc)}
for k, v in missao.items():
    if (k[3], k[4]) in MV: MV[(k[3], k[4])][lix[k[:3]]] += v


def vec(c, n):
    if c in ('1', '5'): return MV.get((c, n), np.zeros(NLc))
    return MAT[c][:, COLS[c].index(n)].astype(float)


MINW = 30


def partners(c, n, k=6):
    a = vec(c, n); A_ = a.sum()
    res = []
    for oc in ('6', '7'):
        if oc == c: continue
        M = MAT[oc]; tot = M.sum(0)
        keep = np.array([len(x) > 2 for x in COLS[oc]]) & (tot >= 1000)
        mask = (W[c] >= MINW) & (W[oc] >= MINW)
        pa = a[mask] / W[c][mask]
        pb = M[mask][:, keep] / W[oc][mask][:, None]
        za = (pa - pa.mean()) / (pa.std() + 1e-12)
        zb = (pb - pb.mean(0)) / (pb.std(0) + 1e-12)
        corr = (za[:, None] * zb).mean(0)
        ov = np.minimum(a[:, None] / max(A_, 1), M[:, keep] / tot[keep]).sum(0)
        nums = [x for x, kk in zip(COLS[oc], keep) if kk]
        for j in np.argsort(-corr)[:k]:
            res.append((oc, nums[j], float(corr[j]), float(ov[j])))
    res.sort(key=lambda x: -x[2])
    return res[:k]


# Missão candidates + partners
PART = {}
for x in cands:
    if x['c'] in ('6', '7', '5', '1') and (len(x['n']) > 2 or x['c'] == '1') and x['v'] >= 1000:
        PART[(x['c'], x['n'])] = partners(x['c'], x['n'])
        print('partners', x['c'], x['n'], x['nm'], [(INFO.get((p[0], p[1]), {}).get('nm'), round(p[2], 2)) for p in PART[(x['c'], x['n'])][:3]])

page_c = []; pidx = {}


def add(c, n, missao_flag):
    if (c, n) in pidx: return pidx[(c, n)]
    a = vec(c, n); nz = np.nonzero(a)[0]
    if c in ('1', '5'):
        nm_, st_ = {('5', '144'): ('RICARDO SCHIAVETTO', 'Não eleito')}.get((c, n)) or st.get((c, n), (names.get((c, n), n), ''))[:2]
        meta = dict(nm=nm_, par='MISSÃO', st=st_, v=int(a.sum()))
    else:
        meta = INFO.get((c, n), dict(nm=names.get((c, n), n), par='?', st='', v=int(a.sum())))
    if len(n) == 2 and c != '1': meta = dict(meta, nm='Voto de legenda (14)' if n == '14' else meta['nm'])
    pidx[(c, n)] = len(page_c)
    page_c.append(dict(c=c, n=n, nm=meta['nm'], par=meta['par'], st=meta['st'], v=int(a.sum()), m=missao_flag,
                       i=[int(v) for v in np.diff(nz, prepend=0)], q=[int(a[i]) for i in nz]))
    return pidx[(c, n)]


for x in cands:
    if x['c'] in ('6', '7', '5', '1'): add(x['c'], x['n'], 1)
for key, ps in PART.items():
    for oc, on, _, _ in ps: add(oc, on, 0)
partners_out = {str(pidx[key]): [[pidx[(oc, on)], round(r, 3), round(o, 3)] for oc, on, r, o in ps] for key, ps in PART.items()}

out_locs = []; approx = 0
for k in locs:
    li = LOC.get(k)
    if li is None:
        mn, nm_, end = A['locinfo'].get(k, ('?', 'Local ' + k[2], ''))
        li = dict(mun=mn, nome=nm_, bairro='', eleitores=0, lat=None, lon=None)
    lat, lon, ap = li['lat'], li['lon'], 0
    if lat is None:
        cc = cent.get(tse2ibge.get(k[0])) or (-23.55, -46.63)
        lat, lon, ap = cc[0], cc[1], 1; approx += 1
    out_locs.append([round(lat, 5), round(lon, 5), midx[li['mun']], li['nome'].strip(), (li['bairro'] or '').strip(),
                     li['eleitores'], int(W['6'][lix[k]]), int(W['7'][lix[k]]), int(W['5'][lix[k]]), ap, int(k[1]), int(W['1'][lix[k]])])
print('locais', len(out_locs), 'aproximados', approx, 'cands na página', len(page_c))

DATA = dict(locs=out_locs, muns=muns, cands=page_c, partners=partners_out,
            valid={c: int(W[c].sum()) for c in ('6', '7', '5', '1')})
json.dump(DATA, open(os.path.join(OUTD, 'missao_data.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 3), round(c[1], 3)]


for ft in geo['features']:
    ft['geometry']['coordinates'] = rnd(ft['geometry']['coordinates'])
json.dump(geo, open(os.path.join(OUTD, 'sp_mun_small.geojson'), 'w'), separators=(',', ':'))
