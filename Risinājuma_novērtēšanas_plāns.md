# Risinājuma novērtēšanas plāns
**Dokumenta statuss:** Melnraksts  
## 1. daļa - Funkcionālo prasību novērtēšana
Lietotāju stāsti ir sadalīti četrās novērtēšanas grupās. Katrai grupai ir viens īss novērtēšanas mērķis un atsevišķi akceptēšanas kritēriji katrai US.

### Testa dati (references gadījumi)

Visi laiki ir minūtēs; katrai grāmatai ir viens pasūtījums. Visām iekārtām: maksimālais nepārtrauktas drukāšanas laiks **480 min**, apkopes ilgums **60 min**.

**Apkopes noteikums** (pēc prasību piemēra): pēc katrām 480 min drukāšanas ir 60 min apkope; pēc pēdējā drukāšanas posma apkope nav vajadzīga. Prasību piemērs: 12 h pieejamas, 4 h drukāšana, 1 h apkope → 4 + 1 + 4 + 1 + 2 = 10 h drukāšanai un 2 h apkopei.

| Grāmata | Peļņa par vienību | Min. tirāža | Druka (min/gab.) | Griešana (min/gab.) | Šūšana (min/gab.) | Apdare (min/gab.) |
|---|---|---|---|---|---|---|
| Ziemas pasakas | 4,50 | 200 | 2,0 | 0,5 | 1,0 (R2: **3,0**) | 0,8 |
| Rīgas vēsture | 7,00 | 100 | 4,0 | 1,0 | 2,5 | 1,5 |
| Programmēšana Python valodā | 5,20 | 150 | 3,0 | 0,8 | 1,5 | 1,2 |

| Iekārta | Kopējais laiks R1 | R1: drukāšana / apkope / atlikums | Kopējais laiks R2 | R2: drukāšana / apkope / atlikums |
|---|---|---|---|---|
| Druka | 2400 | 2160,0 / 240 / 0,0 | 2400 | 2160,0 / 240 / 0,0 |
| Griešana | 1200 | 547,5 / 60 / 592,5 | 1200 | 557,6 / 60 / 582,4 |
| Šūšana | 1800 | 1130,0 / 120 / 550,0 | **2000** | 1820,0 / 180 / 0,0 |
| Apdare | 1500 | 854,0 / 60 / 586,0 | 1500 | 853,6 / 60 / 586,4 |

| Gadījums | Ziemas pasakas | Rīgas vēsture | Programmēšana Python valodā | Kopējā peļņa |
|---|---|---|---|---|
| **R1** (vienkāršs, šaurais posms Druka) | 655 | 100 | 150 | 4427,50 |
| **R2** (divi šaurie posmi Druka un Šūšana) | 344 | 104 | 352 | 4106,40 |

Abiem gadījumiem ir viens optimālais atrisinājums. Daudzumi ir veseli skaitļi; laiku un peļņu salīdzina ar precizitāti 0,01.

**Ko gadījumi atklāj:**

1. Ja apkope netiek ņemta vērā, R1 dod 775 / 100 / 150 (4967,50), bet R2 dod 374 / 104 / 412.
2. Ja modelis rēķina ar daļskaitļiem un noapaļo uz leju, R2 dod 345 / 100 / 356 (4103,70, nav optimāls); ja noapaļo uz tuvāko skaitli, R2 dod 345 / 100 / 357, kas pārsniedz Drukas un Šūšanas drukāšanas laiku.

**Neizpildāmības variants (R1 dati):** Druka kopējais laiks **1350 min**. Bez apkopes laika pietiktu (minimālajām tirāžām vajag 1250 min drukāšanas), bet ar apkopi drukāšanai paliek tikai 1230 min (480 + 60 + 480 + 60 + 270), tāpēc sagaidāmais statuss ir `infeasible`.

### 1. Datu ievade un pārvaldība

**Mērķis:** Novērtēt, vai lietotājs var ievadīt un pārvaldīt drukāšanas plāna aprēķinam nepieciešamos datus, tostarp iekārtu apkopes parametrus.

> Šajā grupā pārbauda datu ievadi, saglabāšanu, rediģēšanu un apkopes parametru norādīšanu.

#### US1 - Must have

**Lietotāja stāsts:** Ražošanas plānotājs vēlas pievienot grāmatu pasūtījumus, jo tie ir nepieciešami drukāšanas plāna izveidošanai.

**Saistītā funkcionālā prasība:** F1

| Nr. | Akceptēšanas kritērijs | Kā pārbaudīsim |
|---|---|---|
| 1.1 | Izvēloties grāmatu, ievadot min. tirāžu 100 un nospiežot pievienošanas pogu, pasūtījums parādās sarakstā un paliek tur pēc lapas pārlādes | Manuāla pārbaude |
| 1.2 | Pasūtījumu ar neeksistējošu grāmatu nevar saglabāt, un tiek parādīts kļūdas ziņojums | Automātisks API tests |
| 1.3 | Pēc trīs pasūtījumu pievienošanas (R1 dati) sarakstā redzami visi trīs ar pareizu grāmatas nosaukumu un min. tirāžu | Manuāla pārbaude |

#### US2 - Must have

**Lietotāja stāsts:** Ražošanas plānotājs vēlas norādīt katras grāmatas peļņu par vienību, jo sistēmai ir jāspēj maksimizēt kopējo peļņu.

**Saistītā funkcionālā prasība:** F2

| Nr. | Akceptēšanas kritērijs | Kā pārbaudīsim |
|---|---|---|
| 2.1 | Grāmatu ar peļņu 5,50 var saglabāt, un sarakstā redzama vērtība 5,50 | Manuāla pārbaude |
| 2.2 | Negatīva peļņa (-1) vai teksts tiek noraidīts ar kļūdas ziņojumu, un ieraksts netiek izveidots | Automātisks API tests |

#### US3 - Must have

**Lietotāja stāsts:** Ražošanas plānotājs vēlas norādīt minimālo drukājamo grāmatu skaitu, jo drukāšanas plānam ir jāievēro pasūtījumu ierobežojumi.

**Saistītā funkcionālā prasība:** F3

| Nr. | Akceptēšanas kritērijs | Kā pārbaudīsim |
|---|---|---|
| 3.1 | Min. tirāža pieņem tikai veselu skaitli, lielāku par 0; vērtības 0, -5 un 2,5 tiek noraidītas | Automātisks API tests |
| 3.2 | Aprēķinātajā plānā katra pasūtījuma daudzums ir vesels skaitlis un ≥ tā min. tirāža | Automātisks tests ar R1 un R2 |

#### US4 - Must have

**Lietotāja stāsts:** Ražošanas plānotājs vēlas norādīt pieejamās drukāšanas iekārtas, jo drukāšanas plānam ir jāņem vērā pieejamās iekārtas.

**Saistītā funkcionālā prasība:** F4

| Nr. | Akceptēšanas kritērijs | Kā pārbaudīsim |
|---|---|---|
| 4.1 | Pievienotā iekārta parādās sarakstā un paliek tur pēc lapas pārlādes | Manuāla pārbaude |
| 4.2 | Iekārtu ar nosaukumu, kas īsāks par 2 rakstzīmēm, nevar saglabāt, un tiek parādīts kļūdas ziņojums | Automātisks API tests |

#### US5 - Must have

**Lietotāja stāsts:** Ražošanas plānotājs vēlas norādīt katras iekārtas kopējo pieejamo laiku, jo plānošanā jāņem vērā gan drukāšana, gan apkopes pārtraukumi.

**Saistītā funkcionālā prasība:** F5

| Nr. | Akceptēšanas kritērijs | Kā pārbaudīsim |
|---|---|---|
| 5.1 | Kopējais pieejamais laiks pieņem tikai skaitli, lielāku par 0; vērtības 0 un -10 tiek noraidītas | Automātisks API tests |
| 5.2 | Aprēķinātajā plānā katrai iekārtai drukāšanas laiks + apkopes laiks nepārsniedz kopējo pieejamo laiku | Automātisks tests ar R1 un R2 |

#### US6 - Must have

**Lietotāja stāsts:** Ražošanas plānotājs vēlas norādīt katrai grāmatai nepieciešamo iekārtas darbības laiku, jo sistēmai ir jāņem vērā iekārtu noslodze.

**Saistītā funkcionālā prasība:** F6

| Nr. | Akceptēšanas kritērijs | Kā pārbaudīsim |
|---|---|---|
| 6.1 | Katram grāmatas un iekārtas pārim var ievadīt apstrādes laiku, un tas paliek saglabāts pēc lapas pārlādes | Manuāla pārbaude |
| 6.2 | Atkārtota ievade tam pašam pārim atjaunina vērtību, nevis izveido dublikātu | Automātisks API tests |
| 6.3 | Negatīvs apstrādes laiks tiek noraidīts ar kļūdas ziņojumu | Automātisks API tests |

#### US11 - Should have

**Lietotāja stāsts:** Ražošanas plānotājs vēlas rediģēt iepriekš ievadītos grāmatu un iekārtu datus, jo sākotnējā informācija var mainīties.

**Saistītā funkcionālā prasība:** F11

| Nr. | Akceptēšanas kritērijs | Kā pārbaudīsim |
|---|---|---|
| 11.1 | Pēc grāmatas peļņas rediģēšanas jaunā vērtība redzama sarakstā un tiek izmantota nākamajā aprēķinā | Manuāla pārbaude |
| 11.2 | Pēc iekārtas kopējā laika rediģēšanas jaunā vērtība redzama sarakstā pēc lapas pārlādes | Manuāla pārbaude |
| 11.3 | Rediģējot neeksistējošu ierakstu, tiek atgriezta kļūda, un dati netiek mainīti | Automātisks API tests |

#### US13 - Must have

**Lietotāja stāsts:** Ražošanas plānotājs vēlas norādīt katras iekārtas nepārtrauktas drukāšanas laiku līdz obligātajai apkopei un apkopes ilgumu, jo drukāšanas plānā jāņem vērā apkopes radītie pārtraukumi.

**Saistītā funkcionālā prasība:** F13

| Nr. | Akceptēšanas kritērijs | Kā pārbaudīsim |
|---|---|---|
| 13.1 | Katrai iekārtai var ievadīt nepārtrauktas drukāšanas laiku un apkopes ilgumu, un abas vērtības paliek saglabātas pēc lapas pārlādes | Manuāla pārbaude |
| 13.2 | Nepārtrauktas drukāšanas laiks pieņem tikai skaitli, lielāku par 0; apkopes ilgums pieņem tikai skaitli, ne mazāku par 0 | Automātisks API tests |
| 13.3 | Prasību piemērs: viena iekārta ar kopējo laiku 720 min, nepārtrauktu drukāšanu 240 min un apkopi 60 min; viena grāmata (1 min/gab., peļņa 1,00, min. tirāža 1). Plānā ir 600 gab., drukāšanas laiks 600 min, apkopes laiks 120 min, atlikums 0 | Automātisks tests un manuāla pārbaude |

### 2. Drukāšanas plāna optimizācija

**Mērķis:** Novērtēt, vai sistēma aprēķina peļņu maksimizējošu drukāšanas plānu, ievērojot pasūtījumu minimālos daudzumus, iekārtu pieejamo laiku un obligātās apkopes pārtraukumus.

> Pārbaudēs jāņem vērā, ka iekārtas kopējais pieejamais laiks ietver arī apkopes pārtraukumus.

#### US7 - Must have

**Lietotāja stāsts:** Ražošanas plānotājs vēlas iegūt optimālu drukāšanas plānu, jo nepieciešams maksimizēt peļņu, ievērojot pasūtījumu minimālos daudzumus, iekārtu pieejamo laiku un apkopes pārtraukumus.

**Saistītā funkcionālā prasība:** F7

| Nr. | Akceptēšanas kritērijs | Kā pārbaudīsim |
|---|---|---|
| 7.1 | Ar R1 datiem sistēma atgriež statusu `optimal` un daudzumus 655 / 100 / 150, kopējā peļņa 4427,50 | Automātisks tests un manuāla pārbaude |
| 7.2 | Ar R2 datiem sistēma atgriež statusu `optimal` un daudzumus 344 / 104 / 352, kopējā peļņa 4106,40 | Automātisks tests |
| 7.3 | Ja Druka kopējais laiks ir 1350 min (R1 dati), sistēma atgriež statusu `infeasible`, un saskarne rāda saprotamu paziņojumu, nevis tehnisku kļūdu | Automātisks tests un manuāla pārbaude |
| 7.4 | Ja nav pasūtījumu, iekārtu vai apstrādes laiku, saskarne rāda paziņojumu par trūkstošajiem datiem | Manuāla pārbaude |

### 3. Rezultātu attēlošana

**Mērķis:** Novērtēt, vai sistēma korekti attēlo aprēķināto drukāšanas plānu, kopējo peļņu un iekārtu noslodzi, tostarp apkopes laiku.

> Šajā grupā pārbauda lietotājam parādītās aprēķina rezultātu vērtības.

#### US8 - Must have

**Lietotāja stāsts:** Ražošanas plānotājs vēlas redzēt, kuras grāmatas un kādā daudzumā ir jādrukā, jo nepieciešams zināt, kurus pasūtījumus ir izdevīgi ražot.

**Saistītā funkcionālā prasība:** F8

| Nr. | Akceptēšanas kritērijs | Kā pārbaudīsim |
|---|---|---|
| 8.1 | Pēc aprēķina tabulā katram pasūtījumam ir viena rinda ar grāmatas nosaukumu un drukājamo daudzumu (R1: 655 / 100 / 150) | Manuāla pārbaude |
| 8.2 | Tabulā redzamie daudzumi sakrīt ar API atbildi | Manuāla pārbaude, salīdzinot ar pārlūka izstrādātāja rīkiem |

#### US9 - Must have

**Lietotāja stāsts:** Ražošanas plānotājs vēlas redzēt aprēķināto kopējo peļņu, jo nepieciešams novērtēt izveidotā drukāšanas plāna rezultātu.

**Saistītā funkcionālā prasība:** F9

| Nr. | Akceptēšanas kritērijs | Kā pārbaudīsim |
|---|---|---|
| 9.1 | Kopējā peļņa ir vienāda ar Σ(daudzums × peļņa par vienību) | Automātisks tests ar R1 un R2 |
| 9.2 | Ar R1 datiem saskarnē redzama kopējā peļņa 4427,50 | Manuāla pārbaude |

#### US10 - Should have

**Lietotāja stāsts:** Ražošanas plānotājs vēlas redzēt katras iekārtas drukāšanas laiku, apkopes laiku un atlikušo pieejamo laiku, jo nepieciešams novērtēt iekārtu noslodzi.

**Saistītā funkcionālā prasība:** F10

| Nr. | Akceptēšanas kritērijs | Kā pārbaudīsim |
|---|---|---|
| 10.1 | Katrai iekārtai redzams drukāšanas laiks, apkopes laiks un atlikušais laiks | Manuāla pārbaude |
| 10.2 | Ar R1 datiem vērtības sakrīt ar testa datu tabulu (piemēram, Druka 2160,0 / 240 / 0,0) | Automātisks tests un manuāla pārbaude |
| 10.3 | Katrai iekārtai drukāšanas laiks + apkopes laiks + atlikums = kopējais pieejamais laiks | Automātisks tests ar R1 un R2 |

### 4. Drukāšanas plānu saglabāšana (neobligāta)

**Mērķis:** Novērtēt, vai lietotājs var saglabāt un atkārtoti apskatīt iepriekš aprēķinātos drukāšanas plānus.

> US12 ir Could have. Šo grupu var neiekļaut gala novērtējumā, ja funkcija netiek realizēta.

#### US12 - Could have

**Lietotāja stāsts:** Ražošanas plānotājs vēlas saglabāt un apskatīt iepriekš aprēķinātos drukāšanas plānus, jo tos var būt nepieciešams izmantot vēlāk.

**Saistītā funkcionālā prasība:** F12

| Nr. | Akceptēšanas kritērijs | Kā pārbaudīsim |
|---|---|---|
| 12.1 | Aprēķinātais plāns parādās saglabāto plānu sarakstā un pēc lapas pārlādes atveras ar tiem pašiem daudzumiem un peļņu | Manuāla pārbaude |
| 12.2 | Pēc grāmatas peļņas rediģēšanas iepriekš saglabātais plāns nemainās | Manuāla pārbaude |

---
