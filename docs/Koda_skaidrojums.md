# Kā darbojas mūsu kods — skaidrojums komandai

Šis fails ir domāts mums pašiem: lai jebkurš no komandas varētu atvērt projektu, saprast,
kas kurā failā notiek, un atbildēt uz pasniedzēja jautājumiem. Kā lietotni palaist —
skatīt galveno [README](../README.md).

## 1. Ko lietotne dara (vienā teikumā)

Lietotājs ievada grāmatas, pasūtījumus, iekārtas un apstrādes laikus, nospiež pogu,
un sistēma izrēķina, **cik katras grāmatas drukāt, lai nopelnītu visvairāk**, nepārsniedzot
iekārtu darba laiku.

## 2. Lielā bilde

```
 Pārlūks (HTML + Bootstrap + plan.js)
      │  1. lietotājs atver lapu vai nosūta formu
      ▼
 routes.py  ── 2. saprot, ko lietotājs grib, pārbauda ievadītos datus
      │
      ├──► models.py ──► PostgreSQL     3. saglabā vai nolasa datus
      │
      ├──► optimizer.py (PuLP + CBC)    4. tikai plāna aprēķinam
      │
      ▼
 templates/*.html  ── 5. no datiem izveido HTML lapu un aizsūta atpakaļ pārlūkam
```

Svarīgi: **optimizer.py neko nezina par datu bāzi.** Tas saņem parastus Python sarakstus
un atdod rezultātu. Datus no DB nolasa un rezultātu saglabā `routes.py`.

## 3. Faili pa vienam

| Fails | Ko tas dara vienkāršiem vārdiem | Kad tas strādā |
|---|---|---|
| [app/__init__.py](../app/__init__.py) | «Ieslēdz» lietotni: nolasa `.env`, pieslēdz datu bāzi, reģistrē lapas. Ja DB nav pieejama, rāda lapu ar instrukciju. | vienreiz, palaižot `flask` |
| [app/models.py](../app/models.py) | Apraksta 7 datu bāzes tabulas. Katra Python klase = viena tabula = viens koncepts no konceptu modeļa. | katru reizi, kad lasām vai rakstām datus |
| [app/routes.py](../app/routes.py) | Visas lapas. Katra funkcija atbild uz vienu adresi, piemēram `/books`. Tur arī formu pārbaude un plāna saglabāšana. | katru reizi, kad pārlūks kaut ko pieprasa |
| [app/optimizer.py](../app/optimizer.py) | Matemātika: uzbūvē modeli un liek CBC risinātājam atrast labāko plānu. | tikai nospiežot «Aprēķināt plānu» |
| [app/cli.py](../app/cli.py) | Termināļa komandas `init-db` (izveido DB un tabulas) un `seed` (ievieto demo datus). | tikai, kad tās palaižam ar roku |
| [app/templates/](../app/templates/) | HTML lapu veidnes. `base.html` — kopīgā izvēlne, pārējās — katra sava lapa. | katru reizi, kad jāparāda lapa |
| [app/static/js/plan.js](../app/static/js/plan.js) | Vienīgais mūsu JavaScript: poga «Aprēķināt plānu» nosūta pieprasījumu un parāda kļūdu vai atver plānu. | lapā «5. Aprēķināt plānu» |
| `app/static/vendor/` | Bootstrap (gatavs dizains). Mēs to nerediģējam. | — |
| [requirements.txt](../requirements.txt) | Python bibliotēku saraksts, ko instalē `pip install`. | instalējot |
| `.env` | Datu bāzes adrese un parole. **Nav repozitorijā** — katram savs. Paraugs: `.env.example`. | palaižot |

## 4. Kas notiek, kad nospiež «Pievienot grāmatu»

1. Pārlūks nosūta formu uz adresi `POST /books`.
2. `routes.py` → funkcija `books()` paņem nosaukumu un peļņu no formas.
3. Pārbauda: vai nosaukums nav tukšs, vai tāda grāmata jau nav, vai peļņa ir skaitlis ≥ 0
   (to dara palīgfunkcija `read_number()`; tā pieņem arī komatu, piem. `4,50`).
4. Ja kaut kas nav kārtībā — parāda sarkanu paziņojumu (`flash`) un neko nesaglabā.
5. Ja viss kārtībā — izveido `Book(...)`, saglabā (`db.session.commit()`) un parāda zaļu paziņojumu.
6. Pārlūks atkal atver `/books`, un sarakstā jau redzama jaunā grāmata.

Pasūtījumi, iekārtas un apstrādes laiki strādā tieši tāpat — tikai citi lauki.
Apstrādes laiku tabulu saglabājam vienkāršāk: vecos laikus izdzēšam un ierakstām visu tabulu no jauna.

## 5. Kas notiek, kad nospiež «Aprēķināt plānu»

1. `plan.js` nosūta `POST /api/optimize`.
2. `routes.py` → `run_optimization()` nolasa no DB visus pasūtījumus, iekārtas un laikus
   un pārveido tos vienkāršos sarakstos.
3. Izsauc `optimize(...)` no `optimizer.py`.
4. Ja plānu nevar aprēķināt (nav laiku, minimumi neietilpst iekārtu laikā), atbild ar kļūdas
   tekstu (HTTP 422), un `plan.js` to parāda sarkanā lodziņā.
5. Ja izdevās — saglabā trīs lietas: **plānu** (kopējā peļņa), **plāna rindas** (cik drukāt katram
   pasūtījumam) un **iekārtu noslodzi** (cik minūšu katra iekārta izmantota). Atbild ar plāna numuru.
6. `plan.js` atver lapu `/plans/<numurs>`, kur redzama tabula, peļņa un noslodze.

## 6. Optimizācija vienkāršiem vārdiem

Mēs nevis paši izmēģinām variantus, bet **aprakstām uzdevumu**, un CBC risinātājs atrod labāko atbildi:

- **Ko meklējam:** katram pasūtījumam skaitli `x` — cik grāmatu drukāt. Tikai veselus skaitļus
  (pusi grāmatas nevar izdrukāt), tāpēc tas ir *veselo skaitļu lineārās programmēšanas* (ILP) uzdevums.
- **Ko gribam:** lai `peļņa × x` visiem pasūtījumiem kopā būtu pēc iespējas lielāka.
- **Noteikumi:** `x` nav mazāks par minimumu un nav lielāks par maksimumu (ja tas norādīts);
  katrai iekārtai kopējais laiks nepārsniedz pieejamo.

**Piemērs ar demo datiem** (to der parādīt prezentācijā):

- Ziemas pasakas uz drukas iekārtas dod 4,50 € / 2 min = **2,25 € minūtē** — visizdevīgākā,
  tāpēc abi tās pasūtījumi sasniedz maksimumu (400 un 150).
- Nākamā ir Rīgas vēsture: 7,00 € / 4 min = 1,75 € minūtē — tā saņem atlikušo drukas laiku.
- Python saņem tikai +2: pēdējās 6 minūtēs 2 Python grāmatas (10,40 €) dod vairāk nekā viena Rīgas vēsture (7 €).
  Tieši tāpēc vajadzīgi veseli skaitļi.
- Kopā **4742,40 €**, un drukas iekārta ir noslogota pilnībā — tā ir «šaurā vieta».

Kāpēc ne ģenētiskais algoritms: tas atrod *labu*, bet ne garantēti *labāko* risinājumu.
Mūsu uzdevumam ILP dod precīzu atbildi sekundes daļā (sīkāk — [Lidzigo_risinajumu_parskats.md](../Lidzigo_risinajumu_parskats.md), 4. sadaļa).

## 7. Datu bāze vienkāršiem vārdiem

| Tabula | Ko glabā | Saistīta ar |
|---|---|---|
| `books` | grāmatas nosaukums un peļņa par vienu eksemplāru | — |
| `orders` | pasūtījums: kura grāmata, minimums, maksimums (var būt tukšs) | `books` |
| `machines` | iekārtas nosaukums un cik minūšu tā pieejama | — |
| `processing_times` | cik minūšu iekārta patērē vienai grāmatai (viena rinda katram pārim grāmata–iekārta) | `books`, `machines` |
| `plans` | aprēķinātais plāns: datums un kopējā peļņa | — |
| `plan_lines` | cik grāmatu drukāt katram pasūtījumam šajā plānā | `plans`, `orders` |
| `machine_loads` | cik minūšu katra iekārta izmantota šajā plānā; «atlicis» izrēķina, netiek glabāts | `plans`, `machines` |

Tabulas izveido komanda `flask --app app init-db`. Ja maināt `models.py`, tabulas jāizveido no
jauna: `flask --app app init-db --drop` (izdzēš visus datus!) un tad `flask --app app seed`.

## 8. Biežākās problēmas

| Ko redzat | Ko darīt |
|---|---|
| `Nav norādīts DATABASE_URL` | Nav faila `.env` — nokopējiet `.env.example` kā `.env`. |
| Lapa «Nav pieejama datu bāze» | Palaidiet `flask --app app init-db` un `flask --app app seed`; pārbaudiet, vai PostgreSQL darbojas. |
| `flask` nav atrasts | Nav aktivizēta virtuālā vide: `.venv\Scripts\Activate.ps1` (rindas sākumā jābūt `(.venv)`). |
| `Datu bāzē jau ir dati` pie `seed` | Vispirms `flask --app app init-db --drop`. |
| Terminālī `?` latviešu burtu vietā | Tikai konsoles kodējums, datos viss ir pareizi. |

## 9. Ja gribat pievienot ko jaunu (piemēram, rediģēšanu — F11)

1. **Lapa:** jauna funkcija `routes.py`, piem. `@bp.route("/books/<int:book_id>/edit", methods=["GET", "POST"])`.
2. **Veidne:** jauns fails `templates/book_edit.html` (var nokopēt formu no `books.html`).
3. **Saite:** pievienojiet pogu «Rediģēt» tabulā `books.html`.
4. Ja vajag jaunu lauku DB — pievienojiet to `models.py` un pārveidojiet tabulas (`init-db --drop`).

Pilnāka versija ar rediģēšanu, dzēšanu, plānu vēsturi un testiem jau ir uzrakstīta zarā `alex`
(pagaidām tikai lokāli, GitHub tā nav) — pirms rakstāt no nulles, pajautājiet.

## 10. Vārdnīca

| Vārds | Nozīme |
|---|---|
| **Flask** | Python ietvars tīmekļa lietotnēm: saista adreses (URL) ar Python funkcijām. |
| **Route / maršruts** | Adrese, piem. `/books`, un funkcija, kas uz to atbild. |
| **Veidne (template)** | HTML fails ar vietām datiem, piem. `{{ b.title }}`. Valoda — Jinja. |
| **SQLAlchemy** | Bibliotēka, kas ļauj strādāt ar DB caur Python klasēm, nevis rakstīt SQL. |
| **flash** | Īss paziņojums (zaļš/sarkans), ko parāda nākamajā lapā. |
| **JSON** | Teksta formāts datu apmaiņai starp JavaScript un serveri. |
| **ILP** | Veselo skaitļu lineārā programmēšana — matemātiska metode labākā varianta atrašanai. |
| **PuLP / CBC** | PuLP — Python bibliotēka modeļa aprakstīšanai; CBC — programma, kas to atrisina. |
| **Virtuālā vide (.venv)** | Projekta atsevišķā Python bibliotēku mape, lai tās nejauktos ar citiem projektiem. |
