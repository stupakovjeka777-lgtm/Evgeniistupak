# -*- coding: utf-8 -*-
"""
Устойчивость рейтинга после расширения вселенной со 100 до 148 направлений.
Вопрос: держатся ли новые ниши при смене весов, или они артефакт одной модели?
Сценарии A и B — те же, что в DATA_VALIDATION/SENSITIVITY_ANALYSIS.md.
Сценарий C там опирается на оси (Cashflow, Founder Fit, Asset Light),
которые для новых ниш не считались, поэтому здесь честно используются только A и B.
"""
import csv, os, statistics as st
BASE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(BASE)
O=["test_no_stock","mp_shield","margin_rub","check","weak_field","demand_stab","repeat","speed","logistics","supplier_ru"]
YF={"YF-1":1.0,"YF-2":0.5,"YF-3":0.5,"YF-4":0.5}

def B(r, yf):
    """Нейтральная модель после аудита: убрано дублирование margin_rub↔check,
    снижен вес mp_shield после валидации S8, поднят вес повторных продаж."""
    v=lambda k: float(r[k])
    s=(0.14*v('test_no_stock')+0.12*v('mp_shield')+0.18*v('margin_rub')
       +0.14*v('weak_field')+0.14*v('demand_stab')+0.12*v('repeat')
       +0.08*v('speed')+0.05*v('logistics')+0.03*v('supplier_ru'))
    return round(s-sum(YF[f] for f in yf if f), 2)

rows=[]
for r in csv.DictReader(open(os.path.join(ROOT,'05_SCORING','NICHE_SCORING_MASTER.csv'),encoding='utf-8'),delimiter=';'):
    yf=[x.strip() for x in r['yellow_flags'].split(',')] if r['yellow_flags'] else []
    rows.append(dict(id=r['id'],nisha=r['nisha'],domain=r['domain'],src="базовая сотня",
                     A=float(r['FINAL_SCORE']),Bs=B(r,yf)))
for fn,dom in [('PETS_RETAIL_EXPANSION.csv','PETS_RETAIL'),('THIN_DOMAINS_EXPANSION.csv',None)]:
    for r in csv.DictReader(open(os.path.join(BASE,fn),encoding='utf-8'),delimiter=';'):
        if r['status']!="ПРОШЛА": continue
        yf=[x.strip() for x in r['yf'].split(',')] if r['yf'] else []
        rows.append(dict(id=r['id'],nisha=r['nisha'],domain=dom or r['domain'],
                         src="добор PETS" if dom else "добор тонких",
                         A=float(r['score']),Bs=B(r,yf)))

def ranks(k):
    return {o['id']:i+1 for i,o in enumerate(sorted(rows,key=lambda x:-x[k]))}
rA,rB=ranks('A'),ranks('Bs')
for o in rows:
    o['rA'],o['rB']=rA[o['id']],rB[o['id']]
    o['spread']=abs(o['rA']-o['rB']); o['mean']=(o['rA']+o['rB'])/2

N=len(rows)
print(f"ниш в рейтинге после расширения: {N}\n")
print(f"{'ср.ранг':>8} {'A':>4} {'B':>4} {'разброс':>8}  ниша")
print("-"*88)
for o in sorted(rows,key=lambda x:x['mean'])[:20]:
    mark=" ← новая" if o['src']!="базовая сотня" else ""
    print(f"{o['mean']:>8.1f} {o['rA']:>4} {o['rB']:>4} {o['spread']:>8}  {o['id']} {o['nisha'][:44]}{mark}")

new=[o for o in rows if o['src']!="базовая сотня"]
old=[o for o in rows if o['src']=="базовая сотня"]
print(f"\nмедианный разброс рангов: все {st.median([o['spread'] for o in rows]):.0f} | "
      f"старые {st.median([o['spread'] for o in old]):.0f} | новые {st.median([o['spread'] for o in new]):.0f}")
print(f"новых ниш в ТОП-20 по среднему рангу: "
      f"{sum(1 for o in sorted(rows,key=lambda x:x['mean'])[:20] if o['src']!='базовая сотня')}")
print(f"медианный балл A: старые {st.median([o['A'] for o in old]):.2f} | новые {st.median([o['A'] for o in new]):.2f}")

# смещение: сколько новых ниш попало в каждую четверть рейтинга
q=[0,0,0,0]
srt=sorted(rows,key=lambda x:-x['A'])
for i,o in enumerate(srt):
    if o['src']!="базовая сотня": q[min(3,i*4//N)]+=1
print(f"распределение {len(new)} новых ниш по четвертям рейтинга (A): "
      f"верхняя {q[0]} | вторая {q[1]} | третья {q[2]} | нижняя {q[3]}")
