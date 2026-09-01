# -*- coding: utf-8 -*-
"""
ТОП-6 + N097: пересчёт с Real Customer Evidence.
RCE = 0 везде (контактов нет), вес customer evidence поднят до 45%.
"""
import csv, os
BASE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(BASE)
u={r['id']:r for r in csv.DictReader(open(os.path.join(ROOT,'09_FINAL_REPORT','UNBIASED_DECISION_MATRIX.csv'),encoding='utf-8'),delimiter=';')}
d={r['id']:r for r in csv.DictReader(open(os.path.join(ROOT,'DEMAND_VALIDATION','DECISION_MATRIX.csv'),encoding='utf-8'),delimiter=';')}

TOP6 = ["N052","N099","N022","N089","N077","N053"]   # первые шесть по ADJ среди не-KILL
RE_ENTRY = ["N097"]                                   # возвращена по новому капитальному условию

RCE = {n:0 for n in TOP6+RE_ENTRY}   # контактов нет ни по одной нише

# Попытка опровержения: что нашёл desk research против каждой ниши
FALSIFY = {
"N089":("Заготовки на Ozon дешевле, чем у мастерских: клиент покупает материал на МП и приходит только за печатью. "
        "МНОГИЕ ПРОВАЛИЛИСЬ, НАЧАВ С СУБЛИМАЦИИ - она одна не даёт рентабельности. Сублимация ограничена полиэстером (S39)",
        "Бьёт по главному аргументу ниши: если клиент бросает бизнес, повторных продаж расходки не будет"),
"N052":("Локальные распиловочные производства есть в каждом городе, Competitive Difficulty 7. "
        "Требуется точность размеров: ошибка = брак за свой счёт",
        "Конкуренция ценой и близостью, а не подачей"),
"N099":("80 заводов-производителей в каталоге 2026. Крупные игроки: Русская Трапеза, Стандартпродмаш (проекты под ключ), "
        "Интеграл Плюс. Канал поиска поставщика - отраслевые каталоги Unipack, Поставщики.ру и выставка Продэкспо (S41)",
        "ТОТ ЖЕ ПАТТЕРН, ЧТО УБИЛ N053: B2B ищет поставщика в отраслевом каталоге, а не на классифайде"),
"N022":("Рынок растёт (производство оборудования +15%, 42 млрд руб), но есть крупные профильные игроки: "
        "ТЭХ-Групп, Экодар, Рустехнобизнес (S40). Осваиваемость предметной области 3/10",
        "Цифра 42 млрд относится к промышленной водоподготовке, не к бытовому сегменту"),
"N077":("Канал закупки - дилеры и грантовые процедуры, Channel Fit 5,60. Founder Fit v2 5,25 - худший в ТОП-6",
        "Деньги на рынке есть (76,5 млрд субсидий), взять их через Авито нечем"),
"N053":("Фабрики закупают напрямую с заводов, держат склад и план закупок, ищут поставщика в отраслевых каталогах (S32,S33). "
        "Санкционный перечень - петли, доводчики, ручки, замки, то есть КОРПУСНАЯ фурнитура (S34)",
        "Channel Fit 5,05. Главное доказательство спроса относится к соседней товарной группе"),
"N097":("Семь московских поставщиков с полным складом заявляют прямые поставки с заводов и скидки оптовикам (S42). "
        "Наше преимущество - три единицы против их полного размерного ряда",
        "Обещание срочности может оказаться иллюзией: они тоже отгружают сегодня"),
}

rows=[]
for nid in TOP6+RE_ENTRY:
    r=u[nid]; dm=d[nid]
    demand_cov=float(dm['EVIDENCE_COVERAGE'])/100
    rce=RCE[nid]
    cov=round(0.55*demand_cov + 0.45*(rce/10), 3)
    conf=round(0.5+cov/2, 3)
    raw=float(r['RAW_v2'])
    adj=round(raw*conf, 2)
    fals, impact = FALSIFY[nid]
    rows.append(dict(id=nid, nisha=r['nisha'], kontur=r['kontur'], drayver=r['drayver'],
        MARKET=float(r['MARKET']), CHANNEL_FIT=float(r['CHANNEL_FIT']),
        DEMAND_EVIDENCE=float(r['DEMAND_EVIDENCE']), FOUNDER_FIT=float(r['FOUNDER_FIT_v2']),
        REAL_CUSTOMER_EVIDENCE=rce, popytok=0, kontaktov=0,
        COVERAGE_v3=round(cov*100), CONFIDENCE_v3=conf,
        RAW=raw, ADJUSTED_v3=adj,
        COMPETITIVE_DIFFICULTY=float(r['COMPETITIVE_DIFFICULTY']),
        prev_verdict=r['VERDICT_v2'], falsification=fals, udar=impact))

def verdict(r):
    # ЖЁСТКОЕ ПРАВИЛО: при RCE = 0 максимум PRIORITY VALIDATION
    if r['REAL_CUSTOMER_EVIDENCE']==0:
        if r['CHANNEL_FIT']<6.0: return "WAIT"
        return "PRIORITY VALIDATION"
    return "требует пересчёта после контактов"
for r in rows: r['VERDICT_v3']=verdict(r)

rows.sort(key=lambda r:-r['ADJUSTED_v3'])
for i,r in enumerate(rows,1): r['prioritet_proverki']=i

fields=['prioritet_proverki','id','nisha','kontur','drayver','MARKET','CHANNEL_FIT','DEMAND_EVIDENCE',
        'FOUNDER_FIT','REAL_CUSTOMER_EVIDENCE','popytok','kontaktov','COVERAGE_v3','CONFIDENCE_v3',
        'RAW','ADJUSTED_v3','COMPETITIVE_DIFFICULTY','prev_verdict','VERDICT_v3','falsification','udar']
with open(os.path.join(ROOT,'09_FINAL_REPORT','TOP6_VALIDATION_MATRIX.csv'),'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter=';'); w.writeheader()
    for r in rows: w.writerow({k:r[k] for k in fields})

print(f"{'#':>2} {'ниша':<34}{'MKT':>5}{'CHAN':>6}{'FF':>6}{'RCE':>5}{'cov':>6}{'ADJ':>6}  вердикт")
for r in rows:
    print(f"{r['prioritet_proverki']:>2} {r['nisha'][:33]:<34}{r['MARKET']:>5}{r['CHANNEL_FIT']:>6}"
          f"{r['FOUNDER_FIT']:>6}{r['REAL_CUSTOMER_EVIDENCE']:>5}{r['COVERAGE_v3']:>5}%{r['ADJUSTED_v3']:>6}  {r['VERDICT_v3']}")
print(f"\nразброс ADJUSTED: {min(r['ADJUSTED_v3'] for r in rows)} .. {max(r['ADJUSTED_v3'] for r in rows)}")
print(f"разница 1-2 места: {round(rows[0]['ADJUSTED_v3']-rows[1]['ADJUSTED_v3'],2)}  (порог незначимости 0,30)")
print(f"контактов проведено: {sum(r['kontaktov'] for r in rows)} из {70}")
