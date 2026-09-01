# -*- coding: utf-8 -*-
"""
Отбор TOP-10 из прошедших фильтр.

ПРОБЛЕМА, КОТОРУЮ РЕШАЕТ ЭТОТ СКРИПТ
Чистая сортировка по Product Fit ставит наверх расходники с маржой 800-2000 руб
за единицу. Они честно набирают баллы: перепродажа 10, установки нет,
капитал минимальный, логистика простая, повтор максимальный. Но при весе
маржи 15% низкая абсолютная маржа не мешает попасть в топ.

Полоса значимости в проекте - 0,30 балла (SCORING_SYSTEM.md). Разброс топ-24
укладывается в 0,40. То есть верхние двадцать позиций статистически
неразличимы, и порядок внутри них задаётся шумом, а не данными.

Поэтому применяется тай-брейк внутри незначимой полосы:
  1) полоса кандидатов: PF >= максимум - 0,5
  2) внутри полосы сортировка по абсолютной марже, затем по PF
  3) не более 2 позиций из одной категории - портфельное правило этапа 1
  4) не более 1 позиции на потребительский кластер

ЧЕТВЁРТОЕ ПРАВИЛО ДОБАВЛЕНО ПОСЛЕ ПРОВЕРКИ ПЕРВОГО РЕЗУЛЬТАТА.
Правило "2 на категорию" пропустило B07 (фены и машинки для груминга,
категория SMALLBIZ) и Z01 (ножницы и насадки для груминга, категория PETS)
как две разные позиции. Это один покупатель - груминг-салон - и пересекающийся
ассортимент. Категория не равна покупателю, и портфель, построенный
по категориям, оказался менее диверсифицированным, чем выглядел.

Выводятся ОБА списка: чистый по PF (как задано) и рабочий (с тай-брейком).
"""
import csv, os
from collections import defaultdict
BASE=os.path.dirname(os.path.abspath(__file__))
rows=[r for r in csv.DictReader(open(os.path.join(BASE,'SKU_UNIVERSE_SCORED.csv'),
      encoding='utf-8'),delimiter=';') if r['status']=="ПРОШЁЛ"]
for r in rows: r['PRODUCT_FIT']=float(r['PRODUCT_FIT'])

pure=sorted(rows,key=lambda r:-r['PRODUCT_FIT'])[:10]

top=max(r['PRODUCT_FIT'] for r in rows); band=[r for r in rows if r['PRODUCT_FIT']>=top-0.5]
band.sort(key=lambda r:(-int(r['marzha']), -r['PRODUCT_FIT']))
# потребительский кластер: кто платит, а не к какой категории отнесён товар
CLUSTER={
 "B07":"груминг","Z01":"груминг","Z02":"груминг",
 "I02":"деревообработка","I03":"деревообработка","I08":"деревообработка",
 "I01":"деревообработка","I09":"деревообработка","I14":"деревообработка",
 "C09":"деревообработка","C05":"металлообработка","C12":"металлообработка",
 "R12":"металлообработка","C01":"маркировка","C02":"маркировка","P08":"маркировка",
 "B01":"маркировка","C03":"печать","C04":"печать","C15":"печать","K01":"печать",
 "X08":"печать","X02":"склад","W09":"склад","W03":"склад","X03":"склад",
 "X04":"агро","X05":"агро","C10":"агро","Z10":"агро","X11":"общепит",
 "B13":"тату","K07":"кожа","S03":"единоборства","S02":"единоборства",
}
work=[]; percat=defaultdict(int); seen=set()
for r in band:
    cl=CLUSTER.get(r['id'], "self:"+r['id'])
    if percat[r['kategoriya']]>=2 or cl in seen: continue
    work.append(r); percat[r['kategoriya']]+=1; seen.add(cl)
    if len(work)==10: break

def show(title,lst):
    print(f"\n=== {title} ===")
    print(f"{'#':>3} {'PF':>6} {'марж':>5} {'id':<5}{'категория':<14} товар")
    print("-"*92)
    for i,r in enumerate(lst,1):
        print(f"{i:>3} {r['PRODUCT_FIT']:>6} {r['marzha']:>5} {r['id']:<5}{r['kategoriya']:<14}{r['tovar'][:44]}")

show("TOP-10 ПО ЧИСТОМУ PRODUCT FIT (как задано)", pure)
show("TOP-10 РАБОЧИЙ (тай-брейк по марже внутри полосы, макс 2 на категорию)", work)

print(f"\nполоса кандидатов: PF >= {top-0.5:.2f}, в ней {len(band)} позиций")
print(f"средняя маржа-балл: чистый топ {sum(int(r['marzha']) for r in pure)/10:.1f} | "
      f"рабочий {sum(int(r['marzha']) for r in work)/10:.1f}")
sp=set(r['id'] for r in pure); sw=set(r['id'] for r in work)
print(f"пересечение списков: {len(sp&sw)} из 10")

with open(os.path.join(BASE,'TOP_10_CANDIDATES.csv'),'w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,delimiter=';'); w.writerow(["spisok","mesto","id","kategoriya","tovar","PRODUCT_FIT","marzha_ball"])
    for i,r in enumerate(pure,1): w.writerow(["chistyy_PF",i,r['id'],r['kategoriya'],r['tovar'],r['PRODUCT_FIT'],r['marzha']])
    for i,r in enumerate(work,1): w.writerow(["rabochiy",i,r['id'],r['kategoriya'],r['tovar'],r['PRODUCT_FIT'],r['marzha']])
