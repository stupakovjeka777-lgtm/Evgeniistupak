# -*- coding: utf-8 -*-
"""Повторный аудит полноты после добора. Сравнение с состоянием до."""
import csv, os
from collections import defaultdict, Counter
BASE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(BASE)

base=list(csv.DictReader(open(os.path.join(BASE,'100_INITIAL_DIRECTIONS.csv'),encoding='utf-8'),delimiter=';'))
rej={r['id'] for r in csv.DictReader(open(os.path.join(BASE,'50_REJECTED_NICHES.csv'),encoding='utf-8'),delimiter=';')}
sc={r['id']:float(r['FINAL_SCORE']) for r in csv.DictReader(open(os.path.join(ROOT,'05_SCORING','NICHE_SCORING_MASTER.csv'),encoding='utf-8'),delimiter=';')}
pets=list(csv.DictReader(open(os.path.join(BASE,'PETS_RETAIL_EXPANSION.csv'),encoding='utf-8'),delimiter=';'))
thin=list(csv.DictReader(open(os.path.join(BASE,'THIN_DOMAINS_EXPANSION.csv'),encoding='utf-8'),delimiter=';'))

# ---- единая вселенная
U=[]
for r in base:
    U.append(dict(id=r['id'],domain=r['domain'],nisha=r['nisha'],
                  passed=r['id'] not in rej, score=sc.get(r['id']), src="базовая сотня"))
for r in pets:
    U.append(dict(id=r['id'],domain="PETS_RETAIL",nisha=r['nisha'],
                  passed=r['status']=="ПРОШЛА", score=float(r['score']) if r['score'] else None, src="добор PETS"))
for r in thin:
    U.append(dict(id=r['id'],domain=r['domain'],nisha=r['nisha'],
                  passed=r['status']=="ПРОШЛА", score=float(r['score']) if r['score'] else None, src="добор тонких"))

with open(os.path.join(BASE,'NICHE_UNIVERSE_MASTER.csv'),'w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,delimiter=';'); w.writerow(["id","domain","nisha","proshla_filtr","score","istochnik"])
    for r in sorted(U,key=lambda x:(x['domain'],x['id'])):
        w.writerow([r['id'],r['domain'],r['nisha'],"да" if r['passed'] else "нет",
                    r['score'] if r['score'] is not None else "", r['src']])

# ---- плотность до и после
BEFORE={"B2B_EQUIP":13,"ENGINEERING":13,"CONSTRUCTION":13,"GARDEN_FARM":10,"AUTO":10,"FURNITURE":9,
        "SPORT_HOBBY":8,"PRODUCTION":6,"LOGISTICS_PACK":6,"PETS":5,"TRADE_EQUIP":4,"ENERGY":3}
dom=defaultdict(list)
for r in U: dom[r['domain']].append(r)

print(f"ВСЕЛЕННАЯ: было 100 → стало {len(U)}\n")
print(f"{'домен':<17}{'было':>6}{'стало':>7}{'прошло':>8}{'лучший':>9}   изменение")
print("-"*70)
for d,rs in sorted(dom.items(),key=lambda x:-len(x[1])):
    was=BEFORE.get(d, 0 if d!="PETS_RETAIL" else 0)
    now=len(rs); p=[x for x in rs if x['passed']]
    best=max((x['score'] for x in p if x['score'] is not None),default=0)
    delta=f"+{now-was}" if now>was else "—"
    print(f"{d:<17}{was:>6}{now:>7}{len(p):>8}{best:>9.2f}   {delta}")
print("-"*70)
print(f"{'ИТОГО':<17}{100:>6}{len(U):>7}{sum(1 for r in U if r['passed']):>8}")

# ---- проверка смещения: корреляция плотность ↔ лучший балл
import statistics as st
pairs=[]
for d,rs in dom.items():
    p=[x for x in rs if x['passed'] and x['score'] is not None]
    if p: pairs.append((len(rs), max(x['score'] for x in p)))
def pearson(a,b):
    ma,mb=st.mean(a),st.mean(b)
    num=sum((x-ma)*(y-mb) for x,y in zip(a,b))
    den=(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))**.5
    return num/den if den else 0
r_after=pearson([x[0] for x in pairs],[x[1] for x in pairs])
BEFORE_BEST={"B2B_EQUIP":7.67,"ENGINEERING":8.32,"CONSTRUCTION":7.36,"GARDEN_FARM":8.16,"AUTO":8.12,
             "FURNITURE":8.15,"SPORT_HOBBY":8.00,"PRODUCTION":8.02,"LOGISTICS_PACK":8.22,"PETS":7.66,
             "TRADE_EQUIP":7.86,"ENERGY":7.86}
r_before=pearson([BEFORE[k] for k in BEFORE_BEST],[BEFORE_BEST[k] for k in BEFORE_BEST])
print(f"\nКорреляция «плотность домена ↔ лучший балл»:  было r={r_before:+.2f}  →  стало r={r_after:+.2f}")

# ---- общий рейтинг
allp=sorted([r for r in U if r['passed'] and r['score'] is not None],key=lambda x:-x['score'])
print(f"\n=== ТОП-15 ОБЩЕГО РЕЙТИНГА ({len(allp)} ниш) ===")
for i,r in enumerate(allp[:15],1):
    mark=" ← новая" if r['src']!="базовая сотня" else ""
    print(f"{i:>3}. {r['score']:>5}  {r['id']:<5} {r['domain']:<16} {r['nisha'][:46]}{mark}")
newtop=[ (i,r) for i,r in enumerate(allp,1) if r['src']!="базовая сотня" and i<=20]
print(f"\nновых ниш в ТОП-20: {len(newtop)}")
for i,r in newtop: print(f"  место {i}: {r['id']} {r['nisha'][:50]} ({r['score']})")
