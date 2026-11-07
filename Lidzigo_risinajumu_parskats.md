# Līdzīgo risinājumu pārskats

## 1. Līdzīgie risinājumi

### 1.1. PrintVis

**PrintVis** ir drukas un iepakojuma industrijai paredzēta MIS/ERP sistēma, kas aptver pasūtījumu pārvaldību, ražošanas plānošanu, grafiku veidošanu, ražošanu, materiālus un finanšu procesus.

PrintVis piedāvā automātisku un manuālu plānošanu. Sistēma var ņemt vērā iekārtu kapacitāti, pieejamās darba stundas un plānoto ražošanu. Tiek piedāvāts arī grafisks plānošanas pārskats, kurā iespējams apskatīt iekārtu kapacitāti un plānoto ražošanu.

Mūsu projektam īpaši interesanta ir iespēja veidot ražošanas grafiku un ņemt vērā iekārtu kapacitāti.

**Avoti:**
- https://printvis.com/features/planning-and-scheduling/
- https://printvis.com/solution-landing/

### 1.2. PrintMIS ePRO

**PrintMIS ePRO** ir Print MIS sistēma, kas paredzēta drukas uzņēmumu darba procesu pārvaldībai. Tā nodrošina funkcijas no pasūtījuma un darba uzdevuma izveides līdz ražošanas plānošanai, piegādei, rēķiniem un atskaitēm.

Sistēmā ir atsevišķs **Production Planner**, kas paredzēts iespiedmašīnu, apdares līniju un citu ražošanas resursu plānošanai. Ir arī Job Board, kur iespējams redzēt ražošanas procesa statusus.

Mūsu projektam noderīga ir ideja par pasūtījuma dzīves cikla sasaisti ar ražošanas plānu un resursiem.

**Avoti:**
- https://www.printmis.com/en/print-job-management-software
- https://www.printmis.com/en/print-mis-software

### 1.3. Avanti Slingshot

**Avanti Slingshot** ir drukas uzņēmumiem paredzēta Print MIS sistēma. Tā ietver pasūtījumu pārvaldību, ražošanas plānošanu, grafiku veidošanu, noliktavas un piegādes procesus, rēķinus un atskaites.

Avanti piedāvā arī plānošanas un secības veidošanas funkcijas. Sistēma var integrēties ar ražošanas iekārtām un citām sistēmām, izmantojot JDF. Tas ļauj nodot ražošanas informāciju starp MIS, pirmsdrukas, ražošanas un pēcapstrādes sistēmām.

Mūsu projektam īpaši interesanta ir pasūtījumu plānošanas un ražošanas resursu sasaistīšana.

**Avoti:**
- https://avantisystems.com/
- https://avantisystems.com/wp-content/uploads/2025/05/Avanti-Core-Modules-May-14-2025.pdf

---

## 2. Līdzīgo risinājumu salīdzinājums

| Kritērijs | PrintVis | PrintMIS ePRO | Avanti Slingshot |
|---|---|---|---|
| Pasūtījumu pārvaldība | Jā | Jā | Jā |
| Ražošanas plānošana | Jā | Jā | Jā |
| Iekārtu/resursu plānošana | Jā | Jā | Jā |
| Automātiska vai daļēji automātiska plānošana | Jā | Plānošanas funkcijas ir pieejamas | Plānošanas un secības veidošanas funkcijas |
| Grafiska plāna attēlošana | Jā | Ražošanas/job board pārskati | Plānošanas funkcijas |
| Ražošanas procesa statusu pārvaldība | Jā | Jā | Jā |
| Integrācija ar citām ražošanas sistēmām | Jā | Jā | Jā, tostarp JDF |
| Finanšu/izmaksu funkcijas | Jā | Jā | Jā |
| Specializācija drukas industrijai | Jā | Jā | Jā |

## 3. Novērojumi

Analizētajos risinājumos atkārtojas vairākas funkcijas:

1. pasūtījumu pārvaldība;
2. ražošanas plānošana;
3. iekārtu un citu resursu kapacitātes ņemšana vērā;
4. ražošanas procesa statusu uzraudzība;
5. plāna vizuāla attēlošana;
6. automatizācija un integrācija ar citām sistēmām.

Salīdzinājums rāda, ka mūsu projekta problēma atbilst reālai drukas industrijas plānošanas problēmai. Tajā pašā laikā mūsu studiju projekta risinājumu var veidot šaurāk, koncentrējoties uz drukāšanas pasūtījumu izpildes plānošanu un konkrēto uzdevumā definēto parametru izmantošanu.

---

## 4. Intelektuālais algoritms

### Izvēlētais algoritms: veselo skaitļu lineārā programmēšana (ILP)

Mūsu uzdevums — noteikt, cik eksemplāru katram pasūtījumam drukāt, lai maksimizētu peļņu,
ievērojot minimālos (un, ja norādīti, maksimālos) daudzumus un iekārtu pieejamo laiku.
Gan mērķa funkcija (peļņa), gan visi ierobežojumi (iekārtu laiks) ir **lineāri** attiecībā pret
drukājamajiem daudzumiem, un daudzumi ir **veseli skaitļi**. Tāpēc uzdevums precīzi atbilst
veselo skaitļu lineārās programmēšanas (Integer Linear Programming, ILP) modelim:

- **mainīgie:** `x_o` — drukājamais daudzums pasūtījumam `o`;
- **mērķis:** `max Σ peļņa_o · x_o`;
- **ierobežojumi:** `min_o ≤ x_o ≤ max_o`; `Σ laiks(o, m) · x_o ≤ pieejamais_laiks_m` katrai iekārtai `m`.

Modeli risina **CBC** risinātājs (izmantojot bibliotēku PuLP) ar zaru un robežu metodi
(branch and bound). Atšķirībā no heiristikām tas atrod **pierādāmi optimālu** risinājumu
vai pierāda, ka risinājuma nav (piemēram, minimālie daudzumi neietilpst iekārtu laikā).
Mūsu uzdevuma izmēram (desmiti pasūtījumu, dažas iekārtas) aprēķins aizņem sekundes daļu.

### Apskatītā alternatīva: ģenētiskais algoritms

Viens no algoritmiem, ko var izmantot ražošanas plānošanas problēmām, ir **ģenētiskais algoritms (Genetic Algorithm)**.

Ražošanas plānošanā ir jānosaka, kādā secībā darbi tiek izpildīti un kādi resursi tiem tiek piešķirti. Šāda problēma var kļūt kombinatoriski sarežģīta, jo palielinoties pasūtījumu un iekārtu skaitam, palielinās iespējamo grafiku skaits.

Ģenētiskā algoritma ideja ir izveidot vairākus iespējamos risinājumus, novērtēt tos ar piemērotības funkciju un iteratīvi veidot jaunus risinājumus, izmantojot atlasi, krustošanu un mutāciju.

Mūsu projektā piemērotības funkcijā teorētiski varētu ņemt vērā:

- kopējo ražošanas laiku;
- iekārtu noslodzi;
- pasūtījumu izpildes prioritāti;
- neizpildīto vai nokavēto pasūtījumu skaitu;
- plānoto peļņu.

**Kāpēc izvēlēts ILP, nevis ģenētiskais algoritms.** Ģenētiskais algoritms ir heiristika: tas
atrod labu, bet ne garantēti labāko risinājumu, un rezultāts atkarīgs no nejaušības un
parametriem (populācijas lielums, mutācijas varbūtība). Tas ir piemērots tad, kad uzdevumu nevar
aprakstīt lineāri — piemēram, ja jāplāno darbu **secība** uz iekārtām, pārkārtošanās laiki vai
termiņi. Mūsu pašreizējā uzdevumā secība netiek plānota, tāpēc ILP dod precīzu atbildi ātrāk un
vienkāršāk. Ģenētiskais algoritms paliek kā iespējams paplašinājums, ja sistēmai tiks pievienota
darbu secības plānošana.
