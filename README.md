# Drukāšanas pasūtījumu izpildes plānošana

Tīmekļa lietotne drukāšanas pasūtījumu un ražošanas resursu pārvaldībai. Sistēmas mērķis ir palīdzēt ražošanas plānotājam ievadīt informāciju par grāmatām, pasūtījumiem un iekārtām un turpmāk aprēķināt optimālu drukāšanas plānu.

Šī ir **tehniskā risinājuma 1. versija**, kurā ir realizēta daļa no sistēmas `Must have` funkcionalitātes.

## Realizētā funkcionalitāte

Pašlaik sistēmā ir realizētas šādas funkcijas:

- grāmatu pievienošana;
- grāmatas peļņas uz vienību norādīšana;
- grāmatu datu rediģēšana;
- iekārtu pievienošana;
- iekārtas pieejamā darbības laika norādīšana;
- iekārtu datu rediģēšana;
- datu saglabāšana PostgreSQL datubāzē;
- saglabāto grāmatu un iekārtu attēlošana lietotāja saskarnē.

Pēc lapas pārlādēšanas ievadītie dati tiek atkārtoti ielādēti no PostgreSQL datubāzes.

Lietotnē var arī pievienot pasūtījumus, norādīt apstrādes laikus un pieprasīt optimālu drukāšanas plānu. Optimizācijas modelis un testu palaišana ir aprakstīti [modeļa dokumentācijā](docs/OptimizationModel.md).

## Izmantotās tehnoloģijas

### Servera puse

- **Python** — servera puses programmatūras izstrādei;
- **Flask** — tīmekļa lietotnes un REST API izveidei;
- **PostgreSQL** — sistēmas datu glabāšanai;
- **Psycopg** — Python savienojumam ar PostgreSQL datubāzi;
- **Gunicorn** — Flask lietotnes darbināšanai servera vidē.
- **PuLP un CBC** — optimālo tirāžu aprēķināšanai.

### Klienta puse

- **HTML5** — lietotāja saskarnes struktūrai;
- **CSS3** — lietotāja saskarnes noformējumam;
- **JavaScript** — lietotāja saskarnes funkcionalitātei un saziņai ar Flask API.

### Izstrādes vide

- **Docker**;
- **Docker Compose**.

Docker tiek izmantots, lai Flask lietotni un PostgreSQL datubāzi varētu palaist vienotā un atkārtojamā vidē.

## Projekta struktūra

```text
ProjLab6k/
├── backend/
│   ├── database/
│   │   └── schema.sql
│   ├── app.py
│   ├── db.py
│   ├── optimizer.py
│   └── requirements.txt
│
├── frontend/
│   ├── planner.html
│   ├── app.js
│   └── style.css
│
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── .env.example
├── .gitignore
└── README.md
```

## Prasības lokālai palaišanai

Lai palaistu projektu lokāli, nepieciešams:

- Git;
- Docker Desktop;
- Docker Compose.

Python un PostgreSQL nav nepieciešams instalēt atsevišķi, jo nepieciešamā vide tiek izveidota Docker konteineros.

## Projekta lejupielāde

Klonēt GitHub repozitoriju:

```bash
git clone https://github.com/Fafn1rrr/ProjLab6k.git
```

Atvērt projekta direktoriju:

```bash
cd ProjLab6k
```

## Projekta palaišana

Pārliecināties, ka Docker Desktop ir palaists.

Projekta saknes direktorijā izpildīt:

```bash
docker compose up --build
```

Pirmajā palaišanas reizē Docker automātiski:

1. lejupielādēs nepieciešamos Docker attēlus;
2. izveidos Python vidi;
3. instalēs Python bibliotēkas;
4. izveidos PostgreSQL datubāzi;
5. izveidos datubāzes tabulas;
6. palaidīs Flask lietotni ar Gunicorn.

Kad konteineri ir palaisti, lietotni var atvērt pārlūkprogrammā:

```text
http://localhost:5002
```

## Sistēmas darbības pārbaude

Backend un datubāzes savienojumu var pārbaudīt, atverot:

```text
http://localhost:5002/api/health
```

Veiksmīgas darbības gadījumā tiek atgriezta atbilde:

```json
{
  "status": "ok"
}
```

### Grāmatas pievienošanas pārbaude

1. Atvērt sadaļu **Books**.
2. Ievadīt grāmatas nosaukumu.
3. Norādīt peļņu uz vienību.
4. Nospiest **Add Book**.
5. Grāmata tiek saglabāta PostgreSQL datubāzē un parādīta tabulā.

### Iekārtas pievienošanas pārbaude

1. Atvērt sadaļu **Machines**.
2. Ievadīt iekārtas nosaukumu.
3. Norādīt pieejamo darbības laiku.
4. Nospiest **Add Machine**.
5. Iekārta tiek saglabāta PostgreSQL datubāzē un parādīta tabulā.

Pēc pārlūkprogrammas lapas pārlādēšanas saglabātie dati paliek pieejami.

## Projekta apturēšana

Lai apturētu darbojošos konteinerus, terminālī var izmantot:

```bash
docker compose down
```

Datubāzes dati tiek saglabāti Docker volume un pēc atkārtotas palaišanas nepazūd.

Ja nepieciešams pilnībā izdzēst lokālos datubāzes datus un izveidot tīru datubāzi:

```bash
docker compose down -v
```

Pēc tam projektu var atkārtoti palaist ar:

```bash
docker compose up --build
```

## Optimizācijas priekšnosacījumi

Ja PostgreSQL sējums ir izveidots pirms apkopes migrācijas, piemēro projektā iekļauto migrāciju pirms iekārtu API un optimizācijas izmantošanas.

```bash
docker compose exec -T db psql -U projlab -d projlab -v ON_ERROR_STOP=1 -f /docker-entrypoint-initdb.d/02-machinesmaintain.sql
```

Katrai iekārtai norāda pozitīvu `continuousPrintingTime` un apkopes ilgumu `maintenanceTime` iekārtu API. Piemēram, `PUT /api/machines/1` var nosūtīt `{"name":"Printer","availableTime":12,"continuousPrintingTime":4,"maintenanceTime":1}`. REST API laika vērtības norāda stundās. Katram pasūtītās grāmatas un iekārtas pārim jābūt apstrādes laikam, tostarp skaidri norādītai nullei, ja iekārta nav vajadzīga.

## Tehniskā risinājuma ierobežojumi

Šajā versijā vēl nav realizēta:

- pasūtījumu pilna pārvaldība;
- iekārtu apkopes parametru ievadīšana tīmekļa formā;
- iepriekš aprēķināto drukāšanas plānu saglabāšana.

Šī funkcionalitāte paredzēta nākamajiem projekta izstrādes posmiem.
