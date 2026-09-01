# -*- coding: utf-8 -*-
"""FINAL OUTPUT: 16 полей на товар + распределение по пяти корзинам."""
import csv, os
from collections import defaultdict
BASE=os.path.dirname(os.path.abspath(__file__))
rd=lambda n: list(csv.DictReader(open(os.path.join(BASE,n),encoding='utf-8'),delimiter=';'))

CF={r['id']:r for r in rd('CHANNEL_FIT_BY_PRODUCT.csv')}
SA={r['id']:r for r in rd('STAGE_A_SOURCING.csv')}
UE={r['id']:r for r in rd('UNIT_ECONOMICS.csv')}
SB=defaultdict(list)
for r in rd('STAGE_B_SUPPLIERS.csv'): SB[r['tovar_id']].append(r['postavshchik'])

NISHA={"T01":"N089 сублимация и печать","T02":"N089 сублимация и печать",
       "T03":"N022 водоочистка","T04":"N052 мебельные комплектующие",
       "T05":"N097 складская техника","T06":"N097 складская техника",
       "T07":"N099 упаковочное оборудование","T08":"E18 оборудование для ПВЗ",
       "T09":"N077 оборудование для КФХ","T10":"N053 механизмы трансформации"}
SPEED={"T01":"7 дней","T02":"21 день","T03":"10 дней","T04":"3 дня","T05":"5 дней",
       "T06":"10 дней","T07":"3 дня","T08":"14 дней","T09":"7 дней","T10":"14 дней"}

rows=[]
for pid in UE:
    c,a,u=CF[pid],SA[pid],UE[pid]
    sup=SB.get(pid,[])
    rows.append({
      "1_tovar":c['tovar'], "2_nisha":NISHA[pid], "3_pokupatel":c['pokupatel'],
      "4_gde_ishchet":c['gde_ishchet'], "5_gde_pokupaet":c['gde_pokupaet'],
      "6_avito_podhodit":c['avito_podhodit'], "7_cena_rynka":a['cena_prodazhi'] or "нет данных",
      "8_cena_postavshchika":a['zakupka'] or "нет данных",
      "9_landed_cost":a['landed_cost'] or "нет данных",
      "10_valovaya_marzha":(f"{u['marzha_rub']} руб / {u['marzha_proc']}%" if u['marzha_rub'] else "нет данных"),
      "11_kapital":(f"{u['kapital']} руб" if u['kapital']!="" else "нет данных"),
      "12_MOQ":a['MOQ'], "13_skorost_zapuska":SPEED[pid],
      "14_glavnyy_risk":u['glavnyy_risk'], "15_luchshiy_kanal":c['luchshiy_kanal'],
      "16_supplier_shortlist":(" | ".join(sup) if sup else a['postavshchiki']),
      "id":pid, "KORZINA":u['korzina'], "CHANNEL_FIT":c['CHANNEL_FIT']})

ORD={"AVITO TEST READY":0,"NON-AVITO OPPORTUNITY":1,"ECONOMICALLY WEAK":2,"SUPPLIER RISK":3,"KILL":4}
rows.sort(key=lambda r:(ORD[r['KORZINA']], -float(r['CHANNEL_FIT'])))
F=["id","KORZINA","CHANNEL_FIT"]+[k for k in rows[0] if k[0].isdigit()]
with open(os.path.join(BASE,'FINAL_PRODUCT_MATRIX.csv'),'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=F,delimiter=';'); w.writeheader()
    for r in rows: w.writerow({k:r[k] for k in F})

cur=None
for r in rows:
    if r['KORZINA']!=cur:
        cur=r['KORZINA']; print(f"\n=== {cur} ===")
    print(f"  {r['id']}  {r['1_tovar'][:44]:<46} канал: {r['15_luchshiy_kanal'][:34]}")
print(f"\nвсего товаров: {len(rows)} | поставщиков в shortlist: "
      f"{sum(len(SB.get(r['id'],[])) for r in rows)}")
