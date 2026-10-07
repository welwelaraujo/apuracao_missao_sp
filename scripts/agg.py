"""Stream votacao_secao_2026_SP.csv and aggregate Missão (14) votes per local de votação."""
import zipfile, io, csv, pickle, os, collections, time

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tse')
z = zipfile.ZipFile(os.path.join(D, 'votacao_secao_2026_SP.zip'))
f = io.TextIOWrapper(z.open('votacao_secao_2026_SP.csv'), encoding='latin-1', newline='')
r = csv.reader(f, delimiter=';')
h = next(r); ix = {k: i for i, k in enumerate(h)}
iM, iMn, iZ, iS, iC, iCd, iN, iNm, iQ, iL, iLn, iLe = (ix[k] for k in (
    'CD_MUNICIPIO', 'NM_MUNICIPIO', 'NR_ZONA', 'NR_SECAO', 'CD_CARGO', 'DS_CARGO', 'NR_VOTAVEL', 'NM_VOTAVEL',
    'QT_VOTOS', 'NR_LOCAL_VOTACAO', 'NM_LOCAL_VOTACAO', 'DS_LOCAL_VOTACAO_ENDERECO'))

valid = collections.Counter()      # (mun,zona,local,cargo) -> votos válidos
missao = collections.Counter()     # (mun,zona,local,cargo,nr) -> votos Missão
names = {}                         # (cargo,nr) -> nome
cargos = {}
locinfo = {}                       # (mun,zona,local) -> (municipio, nome local, endereço)
t = time.time(); n = 0
for row in r:
    n += 1
    nr = row[iN]
    if nr in ('95', '96', '97', '98'):
        continue
    c = row[iC]
    if c not in cargos: cargos[c] = row[iCd]
    k = (row[iM], row[iZ], row[iL])
    q = int(row[iQ])
    valid[k + (c,)] += q
    if nr.startswith('14') and (len(nr) == 2 or (c in ('6', '7') and len(nr) in (4, 5)) or (c == '5' and len(nr) == 3) or c in ('1', '3')):
        missao[k + (c, nr)] += q
        names[(c, nr)] = row[iNm]
        if k not in locinfo: locinfo[k] = (row[iMn], row[iLn], row[iLe])
    if n % 5_000_000 == 0:
        print(n, round(time.time() - t), flush=True)
# local info for all locais (for those with no Missão votes we still want a name)
print('rows', n, 'time', round(time.time() - t))
pickle.dump(dict(valid=valid, missao=missao, names=names, cargos=cargos, locinfo=locinfo),
            open(os.path.join(D, 'agg.pkl'), 'wb'))
print('cargos', cargos)
for (c, nr), nm in sorted(names.items()):
    print(c, nr, nm, sum(v for kk, v in missao.items() if kk[3] == c and kk[4] == nr))
