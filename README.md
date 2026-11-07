# Drukāšanas pasūtījumu izpildes plānošana

Tīmekļa lietotne ražošanas plānotājam. Plānotājs ievada grāmatas un to peļņu par vienību,
pasūtījumus ar minimālo drukājamo skaitu, drukas iekārtas ar pieejamo darbības laiku un
katras grāmatas apstrādes laiku uz katras iekārtas. Sistēma aprēķina **optimālu drukāšanas
plānu**: cik eksemplāru katram pasūtījumam izdrukāt, lai kopējā peļņa būtu maksimāla,
neviens minimālais daudzums netiktu izlaists un nevienai iekārtai netiktu pārsniegts
pieejamais laiks. Rezultātā redzami drukājamie daudzumi, kopējā peļņa un iekārtu noslodze.
Katrs aprēķinātais plāns tiek saglabāts datu bāzē.

Komandas biedriem: vienkāršs skaidrojums, kas kurā failā notiek — [docs/Koda_skaidrojums.md](docs/Koda_skaidrojums.md).

## Izmantotās tehnoloģijas

| Slānis | Tehnoloģija |
|---|---|
| Servera puse | Python 3.11+, Flask 3, Flask-SQLAlchemy |
| Datu bāze | PostgreSQL (draiveris psycopg 3) |
| Optimizācija | PuLP + CBC risinātājs (veselo skaitļu lineārā programmēšana) |
| Klienta puse | HTML5, CSS3, JavaScript, Bootstrap 5 (iekļauts repozitorijā, internets nav vajadzīgs) |
| Serveris (izvietošanai) | Gunicorn uz Ubuntu |

Pamatojums — [Tehnoloģiju steks](TehnologijuSteks.md).

## Palaišana lokāli

**Priekšnosacījumi:** Python 3.11 vai jaunāks un darbojošs PostgreSQL serveris (14+).
Datu bāze nav jāveido ar roku — to izdara komanda `init-db`.

### 1. Lejupielādēt kodu un izveidot virtuālo vidi

Windows (PowerShell):
```powershell
git clone https://github.com/Fafn1rrr/ProjLab6k.git
cd ProjLab6k
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux / macOS:
```bash
git clone https://github.com/Fafn1rrr/ProjLab6k.git
cd ProjLab6k
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Ja PowerShell neļauj palaist `Activate.ps1`, izpildiet vienreiz
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

### 2. Norādīt datu bāzes pieejas datus

Nokopējiet `.env.example` kā `.env` (Windows: `copy .env.example .env`, Linux: `cp .env.example .env`)
un ierakstiet savu PostgreSQL lietotāju un paroli:

```
DATABASE_URL=postgresql+psycopg://postgres:JŪSU_PAROLE@localhost:5432/drukas_planosana
```

### 3. Izveidot datu bāzi, tabulas un demonstrācijas datus

```
flask --app app init-db
flask --app app seed
```

Rezultātam jābūt: `Tabulas gatavas.` un `Pievienotas 3 grāmatas, 4 iekārtas, 4 pasūtījumi un apstrādes laiki.`

### 4. Palaist lietotni

```
flask --app app run
```

Atveriet <http://127.0.0.1:5000> un ejiet pa izvēlnes soļiem 1–5. Lai uzreiz redzētu
rezultātu: **5. Aprēķināt plānu → Aprēķināt plānu**.

Lai sāktu ar tukšu datu bāzi: `flask --app app init-db --drop` (izdzēš visus datus).

### Serverī (Ubuntu)

```bash
gunicorn -w 2 -b 0.0.0.0:8000 "app:create_app()"
```

## Realizētās funkcijas

Šī ir **starpversija**: realizētas visas *Must have* prasības un neobligātais maksimālais daudzums.

| Prasība | Kur lietotnē | Statuss |
|---|---|---|
| F1 / US1 pasūtījumu pievienošana | 2. Pasūtījumi | ✅ |
| F2 / US2 peļņa par vienību | 1. Grāmatas | ✅ |
| F3 / US3 minimālais skaits | 2. Pasūtījumi | ✅ |
| F4, F5 / US4, US5 iekārtas un to laiks | 3. Iekārtas | ✅ |
| F6 / US6 laiks uz vienību | 4. Apstrādes laiki | ✅ |
| F7 / US7 optimāls plāns | 5. Aprēķināt plānu | ✅ |
| F8, F9 / US8, US9 daudzumi un kopējā peļņa | plāna lapa | ✅ |
| F10 / US10 izmantotais un atlikušais laiks | plāna lapa, «Iekārtu noslodze» | ✅ |
| F13 / US13 maksimālais daudzums (neobligāts) | 2. Pasūtījumi | ✅ |
| F11 / US11 datu rediģēšana | — | nākamajā versijā |
| F12 / US12 plānu saraksts | — | daļēji: plāns tiek saglabāts un atvērts pēc aprēķina, saraksta vēl nav |

Ja plānu nav iespējams aprēķināt, lietotne paskaidro iemeslu: nav pasūtījumu vai iekārtu,
nav norādīti apstrādes laiki (parāda, kuri) vai minimālie daudzumi neietilpst iekārtu laikā.

## Optimizācijas modelis

- **Mainīgie:** `x_o` — drukājamo grāmatu skaits pasūtījumam `o` (vesels skaitlis).
- **Mērķis:** maksimizēt `Σ peļņa(grāmata_o) · x_o`.
- **Ierobežojumi:** `min_o ≤ x_o ≤ max_o` katram pasūtījumam (`max_o` — ja norādīts); `Σ laiks(grāmata_o, m) · x_o ≤ pieejamais_laiks_m` katrai iekārtai `m`.

Kods: [app/optimizer.py](app/optimizer.py). Visi laiki ir minūtēs. Kāpēc ILP, nevis
ģenētiskais algoritms — [Līdzīgo risinājumu pārskats, 4. sadaļa](Lidzigo_risinajumu_parskats.md).

**Demonstrācijas datu rezultāts:** kopējā peļņa **4742,40 €** (Ziemas pasakas 400 + 150,
Rīgas vēsture 211, Python 152; Druka noslogota pilnībā).

## Datu modelis

Atbilst [konceptu modelim](KonceptuModelis.md); kods — [app/models.py](app/models.py).

| Koncepts | Tabula | Galvenie lauki |
|---|---|---|
| Grāmata | `books` | `title` (unikāls), `profit_per_unit` |
| Pasūtījums | `orders` | `book_id` → books, `min_quantity`, `max_quantity` (var būt tukšs) |
| Iekārta | `machines` | `name` (unikāls), `available_time` (min) |
| Laiks uz vienību | `processing_times` | PK (`book_id`, `machine_id`), `time_per_unit` (min) |
| Drukāšanas plāns | `plans` | `created_at`, `total_profit` |
| Plāna rinda | `plan_lines` | `plan_id` → plans, `order_id` → orders, `quantity` |
| Iekārtas noslodze | `machine_loads` | `plan_id` → plans, `machine_id` → machines, `used_time`; atlikušais laiks — atvasināts |

## Projekta struktūra

```
app/
  __init__.py      lietotnes izveide un datu bāzes kļūdu lapa
  models.py        datu modelis (7 tabulas)
  optimizer.py     optimizācijas modulis (PuLP + CBC), nepiekļūst DB
  routes.py        visas lapas, formas un POST /api/optimize
  cli.py           komandas init-db un seed (demonstrācijas dati)
  templates/       HTML veidnes (Jinja + Bootstrap 5)
  static/          JavaScript (plan.js) un Bootstrap
docs/              skaidrojums komandai
```

## Projekta dokumentācija

- [Līdzīgo risinājumu pārskats](Lidzigo_risinajumu_parskats.md)
- [Prasību formulējums](prasibas.md)
- [Konceptu modelis](KonceptuModelis.md)
- [Tehnoloģiju steks](TehnologijuSteks.md)
- [Izstrādes plāns](IzstradesPlans.md)
