# -*- coding: utf-8 -*-
"""
Фильтр стоп-флагов и скоринг Product Fit по пулу SKU.
Якоря и веса - PRODUCT_FIT_SYSTEM.md.
"""
import csv, os
from collections import Counter, defaultdict
from sku_data import SKU
BASE=os.path.dirname(os.path.abspath(__file__))

W=[("perekup",0.20),("no_install",0.15),("capital",0.15),("marzha",0.15),
   ("speed",0.10),("logistics",0.10),("on_order",0.05),("visual",0.05),("repeat",0.05)]
KEYS=[k for k,_ in W]
assert abs(sum(w for _,w in W)-1.0)<1e-9

# жёсткие: выводят из TOP-10 полностью
HARD={"RF-INSTALL","RF-SERVICE","RF-CAPITAL","RF-ILLIQUID","RF-MP","RF-LICENSE"}
PRICHINA={
 "RF-INSTALL":"без монтажа или выезда товар не продаётся",
 "RF-SERVICE":"основная маржа возникает из работ, а не из разницы цен",
 "RF-CAPITAL":"стартовый капитал выше бюджета проекта",
 "RF-ILLIQUID":"высокая вероятность неликвида",
 "RF-MP":"массово на маркетплейсах по цене, ниже которой перепродавать нечего",
 "RF-LICENSE":"лицензирование, обязательная маркировка или личная ответственность",
}

rows=[]
for cat, items in SKU.items():
    for sid, name, buyer, price, vals, flags, note in items:
        raw=round(sum(vals[i]*w for i,(_,w) in enumerate(W)),2)
        hard=[f for f in flags if f in HARD]
        # авто-понижение: услуга ещё не обязательна, но уже съедает модель
        lean = (not hard) and (vals[0]<5 or vals[1]<5)
        final=round(raw-1.5,2) if lean else raw
        if hard:
            status="ОТСЕЯН"; metka=",".join(hard)
            prich="; ".join(PRICHINA[f] for f in hard)
        elif lean:
            status="SERVICE-LEAN"; metka="авто-понижение -1,5"
            prich="критерий 1 или 2 ниже 5: услуга съедает товарную модель"
        else:
            status="ПРОШЁЛ"; metka=""; prich=""
        rows.append(dict(id=sid, kategoriya=cat, tovar=name, pokupatel=buyer,
            cena_rynka_orientir=price, **{k:vals[i] for i,k in enumerate(KEYS)},
            RAW=raw, PRODUCT_FIT=final, status=status, flagi=metka,
            prichina=prich, zametka=note))

rows.sort(key=lambda r:(-r['PRODUCT_FIT'] if r['status']=="ПРОШЁЛ" else 1, -r['PRODUCT_FIT']))
F=["id","kategoriya","tovar","pokupatel","cena_rynka_orientir"]+KEYS+ \
  ["RAW","PRODUCT_FIT","status","flagi","prichina","zametka"]
with open(os.path.join(BASE,'SKU_UNIVERSE_SCORED.csv'),'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=F,delimiter=';'); w.writeheader()
    for r in rows: w.writerow(r)

n=len(rows); st=Counter(r['status'] for r in rows)
print(f"пул: {n} SKU в {len(SKU)} категориях\n")
print(f"{'статус':<16}{'шт':>5}")
print("-"*22)
for k,v in st.most_common(): print(f"{k:<16}{v:>5}")
print("-"*22)

fl=Counter(f for r in rows for f in r['flagi'].split(',') if f.startswith("RF-"))
print("\nпо стоп-флагам:")
for k,v in fl.most_common(): print(f"  {k:<14}{v:>4}  {PRICHINA[k]}")

passed=[r for r in rows if r['status']=="ПРОШЁЛ"]
print(f"\n=== TOP-15 ПРОШЕДШИХ ===")
print(f"{'PF':>6}  {'id':<5}{'категория':<16} товар")
print("-"*92)
for r in passed[:15]:
    print(f"{r['PRODUCT_FIT']:>6}  {r['id']:<5}{r['kategoriya']:<16}{r['tovar'][:50]}")

bycat=defaultdict(list)
for r in passed: bycat[r['kategoriya']].append(r)
print(f"\nпрошло по категориям (из {len(passed)}):")
for k in SKU:
    p=len(bycat[k]); tot=len(SKU[k])
    print(f"  {k:<16}{p:>3} из {tot:<3} {'█'*p}")
