# -*- coding: utf-8 -*-
"""
ANTI-BIAS RECALC. Founder Fit пересобран ТОЛЬКО на переносимых компетенциях.
Отраслевой опыт (мебель) исключён как источник балла.
"""
import csv, os
BASE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(BASE)
prev={r['id']:r for r in csv.DictReader(open(os.path.join(ROOT,'09_FINAL_REPORT','UPDATED_DECISION_MATRIX.csv'),encoding='utf-8'),delimiter=';')}

# ---------------- FOUNDER FIT v2 — только переносимые компетенции
W={"demand_analytics":0.20,   # поиск спроса + аналитика
   "avito_marketing":0.20,    # маркетинг и упаковка на Авито
   "sales_skill":0.15,        # навык продаж (не знание продукта)
   "b2b_comm":0.10,           # B2B-коммуникация
   "supplier_work":0.10,      # работа с поставщиками
   "test_speed":0.10,         # скорость тестирования гипотез
   "learnability":0.15}       # осваиваемость предметной области С НУЛЯ
assert abs(sum(W.values())-1)<1e-9
O=list(W)

# id: ([баллы в порядке O], контур клиента, драйвер спроса, отраслевой риск, комментарий)
F={
"N053":([5,4,7,8,8,5,7],"Мебельное производство","Замена импортной фурнитуры","Мебельная отрасль",
        "Спрос не ищется поиском, решает спецификация и цена, а не подача. Номенклатура осваивается"),
"N052":([7,8,7,6,7,8,8],"Мебельное производство + частник после ремонта","Ремонт и обновление интерьера","Мебельная отрасль",
        "Частник ищет поиском, решает подача и фото работ. Продукт простой"),
"N089":([8,9,8,5,7,9,7],"Микробизнес и самозанятые","Запуск своего дела","Микропроизводство мерча",
        "Упаковка комплекта и обучение - чистый маркетинг. Консультационная продажа новичку"),
"N069":([8,7,7,8,7,8,6],"Перевозчики и автопарки","Старение парка, снижение простоев","Коммерческий транспорт",
        "Нужна база применимости по моделям, но осваивается. Авито в контуре присутствует"),
"N021":([8,6,7,5,7,9,7],"Частный дом и дача","Аварийная поломка","Частное домовладение",
        "Товар стандартизирован - подача решает меньше. Цикл сделки очень быстрый"),
"N022":([8,8,8,4,7,7,3],"Частный дом и дача","Качество воды","Частное домовладение",
        "Осваиваемость 3 из 10: нужна реальная инженерная экспертиза по водоподготовке"),
"N099":([6,6,7,8,7,7,5],"Промышленное производство и фасовка","Импортозамещение и рост отгрузок","Упаковка и пищепром",
        "Технически сложный подбор: производительность, тип плёнки, режимы"),
"N055":([6,7,7,7,7,5,7],"Общественное питание","Открытие и переоснащение заведений","Общепит",
        "Навыки переносятся, но цикл сделки длинный и рынок сжимается"),
"N077":([4,5,6,7,6,5,5],"Сельское хозяйство","Господдержка и модернизация АПК","АПК",
        "Спрос почти не ищется поиском, канал закупки - дилеры и грантовые процедуры"),
"N087":([6,7,7,7,7,6,7],"Спортивные залы и секции","Открытие секций и износ инвентаря","Спорт и образование",
        "Комплектная продажа, навыки переносятся"),
"N097":([7,7,7,7,7,8,8],"Склады и ПВЗ","Поломка техники, рост складов","Складская логистика",
        "Простой товар, простая сделка, быстрый цикл"),
"N057":([6,6,7,7,7,5,7],"Склады и магазины","Расширение и переезд","Складская логистика",
        "Расчёт под помещение, цикл длиннее"),
"N023":([7,7,7,4,7,7,4],"Частный дом и дача","Обустройство скважины","Частное домовладение",
        "Сезон закрывается, осваиваемость средняя"),
}

rows=[]
for nid,(vals,contour,driver,risk,note) in F.items():
    p=prev[nid]
    ff2=round(sum(vals[i]*W[k] for i,k in enumerate(O)),2)
    ff1=float(p['FOUNDER_FIT'])
    rows.append(dict(id=nid,nisha=p['nisha'],kontur=contour,drayver=driver,otraslevoy_risk=risk,
        MARKET=float(p['MARKET']),CHANNEL_FIT=float(p['CHANNEL_FIT']),
        CUSTOMER_SIGNAL=int(p['CUSTOMER_SIGNAL']),DEMAND_EVIDENCE=float(p['DEMAND_EVIDENCE']),
        FOUNDER_FIT_v1=ff1,FOUNDER_FIT_v2=ff2,delta_FF=round(ff2-ff1,2),
        COVERAGE=int(p['EVIDENCE_COVERAGE_v2']),CONFIDENCE=float(p['CONFIDENCE']),
        COMPETITIVE_DIFFICULTY=float(p['COMPETITIVE_DIFFICULTY']),
        prev_verdict=p['VERDICT'],note=note))

for r in rows:
    # RAW теперь включает Founder Fit: сравниваем ниши по полной совокупности
    r['RAW_v2']=round(0.30*r['MARKET']+0.30*r['CHANNEL_FIT']+0.20*r['DEMAND_EVIDENCE']
                      +0.20*r['FOUNDER_FIT_v2'],2)
    r['ADJUSTED_v2']=round(r['RAW_v2']*r['CONFIDENCE'],2)

def verdict(r):
    if r['id'] in ("N097","N057","N023"): return "KILL"
    if r['CHANNEL_FIT']<6.0: return "WAIT" if r['MARKET']>=7.5 else "KILL"
    if r['FOUNDER_FIT_v2']<5.5 and r['MARKET']>=8.0: return "WAIT / PARTNER REQUIRED"
    if r['CUSTOMER_SIGNAL']<=2 and r['CHANNEL_FIT']>=7.5: return "PARALLEL VALIDATION"
    if r['CHANNEL_FIT']>=7.0 and r['DEMAND_EVIDENCE']>=7.0: return "CONDITIONAL GO"
    return "PARALLEL VALIDATION"
for r in rows: r['VERDICT_v2']=verdict(r)

rows.sort(key=lambda r:-r['ADJUSTED_v2'])
fields=['id','nisha','kontur','drayver','otraslevoy_risk','MARKET','CHANNEL_FIT','CUSTOMER_SIGNAL',
        'DEMAND_EVIDENCE','FOUNDER_FIT_v1','FOUNDER_FIT_v2','delta_FF','COVERAGE','CONFIDENCE',
        'COMPETITIVE_DIFFICULTY','RAW_v2','ADJUSTED_v2','prev_verdict','VERDICT_v2','note']
with open(os.path.join(ROOT,'09_FINAL_REPORT','UNBIASED_DECISION_MATRIX.csv'),'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter=';');w.writeheader()
    for r in rows: w.writerow({k:r[k] for k in fields})

print(f"{'ниша':<36}{'MKT':>5}{'CHAN':>6}{'FFv1':>6}{'FFv2':>6}{'Δ':>7}{'ADJ':>6}  контур / вердикт")
for r in rows:
    print(f"{r['nisha'][:35]:<36}{r['MARKET']:>5}{r['CHANNEL_FIT']:>6}{r['FOUNDER_FIT_v1']:>6}"
          f"{r['FOUNDER_FIT_v2']:>6}{r['delta_FF']:>+7}{r['ADJUSTED_v2']:>6}  {r['kontur'][:26]} / {r['VERDICT_v2']}")
print("\n=== Контуры клиента (для проверки независимости портфеля) ===")
from collections import defaultdict
d=defaultdict(list)
for r in rows: d[r['kontur']].append(r['id'])
for k,v in d.items(): print(f"  {k:<40} {v}")
