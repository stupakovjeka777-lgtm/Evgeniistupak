# -*- coding: utf-8 -*-
"""
Рандомизированный план обзвона 70 контактов против зафиксированной вселенной ниш.
Строится ПОСЛЕ UNIVERSE FROZEN: состав ниш больше не меняется.

Что делает рандомизация и чего не делает.
НЕ делает: не выбирает, кому звонить — контакты ищутся при обзвоне.
ДЕЛАЕТ: задаёт ПОРЯДОК, в котором ниши идут в работу.

Зачем нужен именно порядок. Навык интервьюера растёт по ходу обзвона:
первые разговоры хуже последних. Если ниша идёт подряд в начале, её данные
собраны худшими интервью, и она проиграет не по рынку, а по очерёдности.
Поэтому накладываются два ограничения:
  1) не более 2 подряд контактов одной ниши — иначе интервьюер входит
     в колею и начинает подсказывать ответы;
  2) ни одна ниша не имеет более 65% своих контактов в одной половине списка.

Сид фиксирован: результат воспроизводим, порядок не подобран под ожидания.
"""
import csv, os, random
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
SEED = 2026
TOTAL = 70

# ниша: (название, кто респондент, сегмент, сколько контактов, основание)
PLAN = {
    "N052": ("Мебельные комплектующие", "мебельный цех / частник после ремонта",
             "B2B малый + B2C", 10, "ТОП-6, прошла единый протокол"),
    "N053": ("Механизмы и каркасы", "фабрика мягкой мебели / дилер фурнитуры",
             "B2B промышленный", 10, "ТОП-6, прошла единый протокол"),
    "N077": ("Оборудование для КФХ", "КФХ / ЛПХ",
             "B2B малый", 10, "ТОП-6, прошла единый протокол"),
    "N089": ("Сублимация и печать", "мастерская печати / начинающий мерч",
             "микробизнес", 10, "ТОП-6, прошла единый протокол"),
    "N097": ("Складская техника", "склад / ПВЗ / оптовая база",
             "B2B малый", 10, "ТОП-6, прошла единый протокол"),
    "N099": ("Упаковочное оборудование", "пищевое микропроизводство / фасовщик",
             "B2B промышленный", 10, "ТОП-6, прошла единый протокол"),
    "E18":  ("Оборудование для пунктов выдачи заказов", "владелец или управляющий ПВЗ",
             "B2B малый", 6, "новая из добора: 6-е место по баллу, единый протокол НЕ проходила"),
    "XXX":  ("Независимый кандидат (резерв)", "определяется на месте",
             "любой", 4, "резерв: ниша называется самим респондентом"),
}

assert sum(v[3] for v in PLAN.values()) == TOTAL, "сумма контактов не равна 70"

# ---------------------------------------------------------------- перемешивание
def max_run(seq):
    best = run = 1
    for i in range(1, len(seq)):
        run = run + 1 if seq[i] == seq[i-1] else 1
        best = max(best, run)
    return best

def half_skew(seq):
    """Максимальная доля контактов ниши, попавшая в одну половину списка."""
    h = len(seq) // 2
    worst = 0.0
    for nid, n in Counter(seq).items():
        if nid == "XXX":            # резерв распределять не нужно
            continue
        first = sum(1 for x in seq[:h] if x == nid)
        worst = max(worst, max(first, n - first) / n)
    return worst

pool = [nid for nid, v in PLAN.items() for _ in range(v[3])]
rng = random.Random(SEED)

order, tries = None, 0
while tries < 20000:
    tries += 1
    cand = pool[:]
    rng.shuffle(cand)
    if max_run(cand) <= 2 and half_skew(cand) <= 0.65:
        order = cand
        break
assert order, "ограничения не выполнены за 20000 попыток"

# ---------------------------------------------------------------- запись
FIELDS = ["poryadok","nisha_id","nisha","tip_respondenta","segment","osnovanie",
          "kontakt_nayden","kontakt_sostoyalsya","prichina_otkaza",
          "q1_chto_pokupali","q2_GDE_NASHLI_postavshchika","q3_GDE_KUPILI",
          "q4_alternativy","q5_pochemu_etot_postavshchik","q6_chto_ne_ustraivaet",
          "q7_TRIGGER_SMENY","q8_gde_nachinayut_iskat","q9_avito_12mes",
          "q10_pokupka_cherez_avito","q10_chto_i_na_skolko","q10_pochemu_net",
          "q11_chto_dolzhno_byt_luchshe","citata","signal"]

with open(os.path.join(BASE, 'CONTACT_PLAN_70.csv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=FIELDS, delimiter=';')
    w.writeheader()
    for i, nid in enumerate(order, 1):
        name, resp, seg, _, osn = PLAN[nid]
        row = {k: "" for k in FIELDS}
        row.update(poryadok=i, nisha_id=nid, nisha=name,
                   tip_respondenta=resp, segment=seg, osnovanie=osn)
        w.writerow(row)

# ---------------------------------------------------------------- отчёт
print(f"сид {SEED} | попыток до выполнения ограничений: {tries}")
print(f"максимум подряд одной ниши: {max_run(order)} (порог 2)")
print(f"максимальный перекос по половинам: {half_skew(order):.0%} (порог 65%)\n")

q = len(order) // 4
print(f"{'ниша':<7}{'всего':>7}   распределение по четвертям списка")
print("-" * 58)
for nid, v in sorted(PLAN.items(), key=lambda x: -x[1][3]):
    pos = [i for i, x in enumerate(order) if x == nid]
    quarters = [sum(1 for p in pos if min(3, p // q) == k) for k in range(4)]
    print(f"{nid:<7}{v[3]:>7}   {quarters}")
print("-" * 58)
print(f"{'ИТОГО':<7}{len(order):>7}")
print("\nпервые 12 контактов:")
for i, nid in enumerate(order[:12], 1):
    print(f"  {i:>2}. {nid:<5} {PLAN[nid][0]}")
