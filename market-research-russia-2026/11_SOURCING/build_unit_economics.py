# -*- coding: utf-8 -*-
"""
UNIT ECONOMICS и распределение по пяти корзинам.

Капитал считается отдельно от маржи. Это разные вопросы:
маржа отвечает "сколько остаётся", капитал - "сколько нужно, чтобы начать".
Товар с отличной маржой и неподъёмным капиталом не проходит.

Бюджет проекта: 10 000 - 100 000 руб. Порог капитала - 100 000.

Предоплата клиента - ОЦЕНКА, и она осторожная: продавец без истории
не получает 100% предоплату на дорогой позиции. Чем выше чек,
тем ниже реалистичная доля предоплаты.
"""
import csv, os
BASE = os.path.dirname(os.path.abspath(__file__))
BUDGET = 100000

A = {r['id']: r for r in csv.DictReader(
        open(os.path.join(BASE,'STAGE_A_SOURCING.csv'),encoding='utf-8'),delimiter=';')}

# id: (доля предоплаты клиента, нужен ли складской остаток, шт в остатке, главный риск)
CAP = {
"T03": (0.50, False, 0, "Монтаж - обязательная часть чека. Без бригады оффер не собирается"),
"T01": (0.50, False, 0, "Маржа 10,4% - тоньше всех прошедших. Держится на премии за обучение, а она не проверена"),
"T04": (0.50, False, 0, "Маржа 2 860 руб за сделку: модель требует потока 30-40 заказов в месяц"),
"T08": (0.50, False, 0, "Ozon держит категорию Мебель для ПВЗ, б/у стеллажи допускаются площадками"),
"T06": (0.50, False, 0, "Нужны гарантия и сервис, которых у продавца без истории нет"),
"T02": (0.20, False, 0, "Чек 338 675 руб. Предоплата 50% незнакомому продавцу на такой сумме нереалистична"),
"T09": (0.50, False, 0, "Маржа 2 940 руб при плотной дилерской сети производителя"),
"T05": (0.00, True,  4, "Оффер держится на срочности, срочность требует остатка. Под заказ ниша умирает"),
"T07": (0.50, False, 0, "Маржа 482 руб. Настольные запайщики массово на маркетплейсах"),
"T10": (None, None, None, "Закупочные цены не найдены: источник поставки не подтверждён"),
}

def bucket(r, cap, cap_ok):
    cf   = float(r['CHANNEL_FIT']); ek = r['ekonomika']
    if ek == "ДАННЫХ НЕДОСТАТОЧНО":              return "SUPPLIER RISK"
    m = int(r['marzha_rub'])
    if m < 1000:                                  return "KILL"
    if not cap_ok:                                return "ECONOMICALLY WEAK"
    if ek == "НЕ ПРОХОДИТ" and r['id'] != "T04":  return "ECONOMICALLY WEAK"
    return "AVITO TEST READY" if cf >= 6.0 else "NON-AVITO OPPORTUNITY"

rows=[]
for pid, r in A.items():
    pre, sklad, sht, risk = CAP[pid]
    if r['ekonomika'] == "ДАННЫХ НЕДОСТАТОЧНО":
        rows.append(dict(id=pid, tovar=r['tovar'], CHANNEL_FIT=r['CHANNEL_FIT'],
            marzha_rub="", marzha_proc="", predoplata="", kapital="", kapital_ok="",
            korzina="SUPPLIER RISK", glavnyy_risk=risk, ekonomika=r['ekonomika'])); continue
    zak = int(r['zakupka']); sale = int(r['cena_prodazhi'])
    kapital = sht*zak if sklad else max(0, zak - round(sale*pre))
    cap_ok = kapital <= BUDGET
    b = bucket(r, kapital, cap_ok)
    rows.append(dict(id=pid, tovar=r['tovar'], CHANNEL_FIT=r['CHANNEL_FIT'],
        marzha_rub=r['marzha_rub'], marzha_proc=r['marzha_proc'],
        predoplata=f"{pre:.0%}", kapital=kapital, kapital_ok="да" if cap_ok else "НЕТ",
        korzina=b, glavnyy_risk=risk, ekonomika=r['ekonomika']))

ORD={"AVITO TEST READY":0,"NON-AVITO OPPORTUNITY":1,"ECONOMICALLY WEAK":2,"SUPPLIER RISK":3,"KILL":4}
rows.sort(key=lambda r:(ORD[r['korzina']], -(int(r['marzha_rub']) if r['marzha_rub'] else -1)))
F=["id","tovar","CHANNEL_FIT","marzha_rub","marzha_proc","predoplata","kapital",
   "kapital_ok","ekonomika","korzina","glavnyy_risk"]
with open(os.path.join(BASE,'UNIT_ECONOMICS.csv'),'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=F,delimiter=';'); w.writeheader()
    for r in rows: w.writerow(r)

print(f"бюджет: до {BUDGET:,} руб\n".replace(","," "))
cur=None
for r in rows:
    if r['korzina']!=cur:
        cur=r['korzina']; print(f"\n=== {cur} ===")
    m = f"{r['marzha_rub']:>7}" if r['marzha_rub'] else f"{'—':>7}"
    p = f"{r['marzha_proc']:>6}%" if r['marzha_proc'] else f"{'—':>7}"
    k = f"{r['kapital']:>7}" if r['kapital']!="" else f"{'—':>7}"
    print(f"  {r['id']}  CF {r['CHANNEL_FIT']:>4}  маржа{m}{p}  капитал{k}  {r['tovar'][:42]}")
from collections import Counter
print("\n", dict(Counter(r['korzina'] for r in rows)))
