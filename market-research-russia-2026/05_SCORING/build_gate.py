# -*- coding: utf-8 -*-
"""
FINAL VALIDATION GATE — Channel Fit, Customer Signal, Confidence-Adjusted Score.
Расчёт воспроизводим. Баллы 0-10 экспертные, по якорям, источники указаны.
"""
import csv, os
BASE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(BASE)

prev = {r['id']: r for r in csv.DictReader(
    open(os.path.join(ROOT,'DEMAND_VALIDATION','DECISION_MATRIX.csv'), encoding='utf-8'), delimiter=';')}

# ---------------------------------------------------------- CHANNEL FIT (Авито)
CFW = {  # веса; отличие от предложенных в ТЗ обосновано в CHANNEL_FIT_SCORE.md
 "buyers_use_avito":  0.20,  # покупатели вообще пользуются Авито для этой задачи
 "findable":          0.15,  # покупателя реально найти через Авито
 "listing_fits":      0.10,  # товар удобно представить объявлением  (ТЗ: 15%)
 "switch_readiness":  0.20,  # готовность обратиться к новому поставщику (ТЗ: 15%)
 "remote_deal":       0.10,  # возможна дистанционная сделка
 "adv_over_mp":       0.15,  # преимущество Авито перед маркетплейсами
 "no_stock_start":    0.10,  # можно начать без склада
}
assert abs(sum(CFW.values())-1) < 1e-9
CFO = list(CFW)

CF = {
"N053": ([3,3,6,4,7,8,7], "Фабрики закупают напрямую с заводов и у известных оптовиков, держат склад и план закупок (S32). Поставщика ищут в отраслевых каталогах и на выставках (S33), не на Авито"),
"N052": ([7,7,7,8,5,8,8], "Двойной клиент: мелкие цеха и частник после ремонта. Частник ищет 'столешница на заказ' именно на Авито и постоянного поставщика не имеет"),
"N089": ([9,8,8,9,8,7,7], "Клиент - новичок и микробизнес. Постоянного поставщика нет вообще, первая покупка. На Авито активен рынок нового и б/у оборудования"),
"N022": ([8,8,6,8,6,8,8], "Частный домовладелец ищет решение проблемы поиском и на Авито, поставщика не имеет"),
"N099": ([6,6,7,7,7,7,7], "Малое производство: часть ищет на Авито, часть у профильных поставщиков"),
"N055": ([6,6,7,6,5,8,9], "Заведение ищет мебель на Авито, но при открытии чаще идёт к фабрике напрямую"),
"N021": ([8,8,7,8,7,5,7], "Аварийная покупка, ищут срочно и локально. Но товар компактен - МП рядом"),
"N077": ([4,4,6,6,5,8,7], "Фермер закупает через дилеров и по грантовым процедурам, Авито - не основной канал"),
"N069": ([7,7,7,7,7,7,7], "Перевозчики и автопарки используют Авито регулярно"),
"N087": ([6,6,7,7,6,8,8], "Залы ищут комплекты, часть закупок через бюджетные процедуры"),
"N097": ([7,7,7,7,6,6,5], "Склады ищут срочно и локально - Авито работает, но нужен остаток"),
"N057": ([6,6,6,6,6,8,8], "Расчёт под помещение, чаще идут к профильному поставщику"),
"N023": ([7,7,6,7,6,8,8], "Частник ищет обустройство скважины поиском и на Авито"),
}

# ---------------------------------------------------------- CUSTOMER SIGNAL
# Шкала из ТЗ: 0-2 нет подтверждения / 3-4 слабые / 5-6 повторяющиеся проблемы /
# 7-8 активно ищут альтернативы / 9-10 срочное переключение спроса.
# ИНТЕРВЬЮ НЕ ПРОВЕДЕНЫ НИ ПО ОДНОЙ НИШЕ. Балл выше 2 ставится только там,
# где есть внешнее событие, а не мнение аналитика.
CS = {
"N053": (3, "Косвенный ценовой шок по фурнитуре (S26,S34), но санкционный перечень - петли, доводчики, ручки, замки, то есть КОРПУСНАЯ фурнитура, а не механизмы мягкой мебели. Покупатели не опрошены"),
"N052": (2, "Покупатели не опрошены, внешних событий по нише нет"),
"N089": (2, "Покупатели не опрошены. Отраслевой статистики по нише не существует"),
"N022": (2, "Покупатели не опрошены"),
"N099": (3, "Уход западных поставщиков освободил нишу (S29) - внешнее событие есть, но покупатели не опрошены"),
"N055": (2, "Покупатели не опрошены. Внешний сигнал по рынку отрицательный (S28)"),
"N021": (2, "Покупатели не опрошены"),
"N077": (3, "Грантовые программы обязывают закупать технику (S31) - внешнее событие есть, покупатели не опрошены"),
"N069": (2, "Покупатели не опрошены"),
"N087": (2, "Покупатели не опрошены"),
"N097": (2, "Покупатели не опрошены"),
"N057": (2, "Покупатели не опрошены"),
"N023": (2, "Покупатели не опрошены"),
}

# ---------------------------------------------------------- COVERAGE v2
# 70% веса - сигналы спроса из этапа 1.6, 30% - customer discovery (не проведён нигде).
CD_COVERAGE = 0.0

rows=[]
for nid, (vals, note) in CF.items():
    p = prev[nid]
    cf = round(sum(vals[i]*CFW[k] for i,k in enumerate(CFO)), 2)
    cs, csnote = CS[nid]
    demand_cov = float(p['EVIDENCE_COVERAGE'])/100
    total_cov = round(0.70*demand_cov + 0.30*CD_COVERAGE, 3)
    conf = round(0.5 + total_cov/2, 3)          # 100% -> 1.0 ; 42% -> 0.71
    market = float(p['MARKET'])
    raw = round(0.40*market + 0.35*cf + 0.25*float(p['DEMAND_EVIDENCE']), 2)
    adj = round(raw*conf, 2)
    rows.append(dict(id=nid, nisha=p['nisha'], tip=p['tip'],
        MARKET=market, CHANNEL_FIT=cf, CUSTOMER_SIGNAL=cs,
        DEMAND_EVIDENCE=float(p['DEMAND_EVIDENCE']),
        FOUNDER_FIT=float(p['FOUNDER_FIT']), CASHFLOW=float(p['CASHFLOW']),
        COMPETITIVE_DIFFICULTY=float(p['COMPETITIVE_DIFFICULTY']),
        MARKET_ACTIVITY=float(p['MARKET_ACTIVITY']),
        EVIDENCE_COVERAGE_v2=round(total_cov*100), CONFIDENCE=conf,
        RAW_SCORE=raw, CONFIDENCE_ADJUSTED=adj,
        prev_type=p['TYPE'], prev_decision=p['DECISION'],
        cf_note=note, cs_note=csnote))

# ---------------------------------------------------------- ВЕРДИКТ
def verdict(r):
    # KILL — решения этапа 1.6 не пересматриваются без новых данных
    if r['id'] in ("N097","N057","N023"): return "KILL"
    # Канал не подходит — независимо от качества рынка
    if r['CHANNEL_FIT'] < 6.0:
        return "WAIT" if r['MARKET'] >= 7.5 else "KILL"
    # Сильный рынок при отсутствии фита — нужен партнёр
    if r['FOUNDER_FIT'] < 4.0 and r['MARKET'] >= 8.0: return "WAIT / PARTNER REQUIRED"
    # Никаких GO NOW без опроса покупателей
    if r['CUSTOMER_SIGNAL'] <= 2 and r['CHANNEL_FIT'] >= 7.5: return "PARALLEL VALIDATION"
    if r['CHANNEL_FIT'] >= 7.0 and r['DEMAND_EVIDENCE'] >= 7.0: return "CONDITIONAL GO"
    return "PARALLEL VALIDATION"

for r in rows: r['VERDICT'] = verdict(r)
rows.sort(key=lambda r: -r['CONFIDENCE_ADJUSTED'])

fields=['id','nisha','tip','MARKET','CHANNEL_FIT','CUSTOMER_SIGNAL','DEMAND_EVIDENCE',
        'FOUNDER_FIT','CASHFLOW','MARKET_ACTIVITY','COMPETITIVE_DIFFICULTY',
        'EVIDENCE_COVERAGE_v2','CONFIDENCE','RAW_SCORE','CONFIDENCE_ADJUSTED',
        'prev_type','prev_decision','VERDICT','cf_note','cs_note']
with open(os.path.join(ROOT,'09_FINAL_REPORT','UPDATED_DECISION_MATRIX.csv'),'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter=';'); w.writeheader()
    for r in rows: w.writerow({k:r[k] for k in fields})

print(f"{'ниша':<38}{'MKT':>5}{'CHAN':>6}{'CS':>4}{'cov':>6}{'conf':>6}{'RAW':>6}{'ADJ':>6}  вердикт")
for r in rows:
    print(f"{r['nisha'][:37]:<38}{r['MARKET']:>5}{r['CHANNEL_FIT']:>6}{r['CUSTOMER_SIGNAL']:>4}"
          f"{r['EVIDENCE_COVERAGE_v2']:>5}%{r['CONFIDENCE']:>6}{r['RAW_SCORE']:>6}{r['CONFIDENCE_ADJUSTED']:>6}  {r['VERDICT']}")
