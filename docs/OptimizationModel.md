# Drukāšanas plāna optimizācijas modelis

## 1. Optimizācijas uzdevuma formulējums

Plānošanas periodam nosaka katra pasūtījuma tirāžu, kas maksimizē kopējo peļņu, ievērojot obligātos minimālos tirāžus un katras iekārtas jaudu. Modulis izmanto PuLP un tā komplektācijā iekļauto CBC risinātāju.

## 2. Matemātiskā modeļa parametri

| Apzīmējums | Nozīme |
|---|---|
| $j=1,\ldots,N$ | Pasūtījuma indekss |
| $i=1,\ldots,J$ | Iekārtas indekss |
| $p_j$ | Peļņa par vienu pasūtījuma eksemplāru |
| $q_j^{\min}$ | Obligātā minimālā tirāža |
| $t_{ij}$ | Iekārtas darba laiks viena pasūtījuma eksemplāra izgatavošanai |
| $T_i$ | Kopējais iekārtas pieejamais laiks, ieskaitot apkopes |
| $W_i$ | Maksimālais nepārtrauktas drukāšanas laiks |
| $M_i$ | Vienas apkopes ilgums |
| $T_i^{\mathrm{eff}}$ | Efektīvais drukāšanai pieejamais laiks |

Visi laiki modelī ir minūtēs. PostgreSQL glabā minūtes, un Flask pārveido REST API laika vērtības stundās atbilstoši pašreizējai lietotāja saskarnei.

## 3. Lēmuma mainīgie

$x_j \in \mathbb{Z}_{\ge 0}$ ir pasūtījuma $j$ tirāža. Realizācijā CBC aprēķina papildu tirāžu $y_j = x_j - q_j^{\min}$ pēc minimālās tirāžas rezervēšanas.

## 4. Mērķa funkcija

$$
\max Z = \sum_{j=1}^{N} p_j x_j
$$

Minimālo tirāžu peļņa ir konstanta. Risinātājā maksimizē papildu tirāžu peļņu un rezultātā iekļauj arī minimālo tirāžu peļņu.

## 5. Ierobežojumi

$$
x_j \ge q_j^{\min} \qquad \forall j
$$

$$
\sum_{j=1}^{N} t_{ij} x_j \le T_i^{\mathrm{eff}} \qquad \forall i
$$

Modeļa maksimālo tirāžu nosaka iekārtu jauda. Pirms CBC izsaukšanas modulis precīzi pārbauda, vai pietiek jaudas visu minimālo tirāžu izpildei. Iekārtu ierobežojumus pārveido veselu koeficientu formā pēc minimālajiem tirāžiem vajadzīgā laika atskaitīšanas.

## 6. Iekārtu tehniskās apkopes modelis

Efektīvo laiku katrai iekārtai aprēķina pirms optimizācijas.

$$
C_i = \left\lfloor \frac{T_i}{W_i + M_i} \right\rfloor, \qquad
R_i = T_i - C_i(W_i + M_i), \qquad
T_i^{\mathrm{eff}} = C_i W_i + \min(R_i, W_i)
$$

Pēc tirāžu noteikšanas aprēķina drukāšanas laiku $P_i$, apkopju skaitu $K_i$, apkopes laiku $S_i$, izmantoto laiku $U_i$ un atlikumu $L_i$.

$$
P_i = \sum_{j=1}^{N} t_{ij}x_j, \qquad
K_i = \max\left(0,\left\lceil \frac{P_i}{W_i} \right\rceil - 1\right)
$$

$$
S_i = K_i M_i, \qquad U_i = P_i + S_i, \qquad L_i = T_i - U_i
$$

$$
\mathrm{Noslodze}_i =
\begin{cases}
100\, U_i / T_i, & T_i > 0 \\
0, & T_i = 0
\end{cases}
$$

Apkopi veic pirms nākamā drukāšanas posma, kad sasniegts limits $W_i$. Ja pēdējais posms beidzas tieši pie limita, papildu apkope nav vajadzīga. Aprēķinos izmanto precīzu decimālo ievades vērtību racionālo attēlojumu, lai pie limita nepieskaitītu lieku apkopi. Pirms rezultāta atgriešanas modulis pārbauda $P_i \le T_i^{\mathrm{eff}}$ un $U_i \le T_i$.

## 7. Ievaddati un izvaddati

| Parametrs | Ieraksta lauki |
|---|---|
| Pasūtījumu saraksts | `id`, `book_id`, `profit_per_unit`, `min_quantity` |
| Iekārtu saraksts | `id`, `available_time`, `continuous_printing_time`, `maintenance_time` |
| Apstrādes laiku saraksts | `book_id`, `machine_id`, `time` |

Identifikatori var būt veseli skaitļi vai netukšas virknes. Laiki un peļņa ir galīgi `int`, `float` vai `Decimal` skaitļi. Minimālā tirāža ir pozitīvs vesels skaitlis, kā noteikts pasūtījumu datu modelī. Katram pasūtījumos iekļautās grāmatas un iekārtas pārim norāda tieši vienu apstrādes laiku. Nulle nozīmē, ka attiecīgā iekārta grāmatai nav nepieciešama. Vairāki vienas grāmatas pasūtījumi izmanto vienus un tos pašus apstrādes laikus.

Rezultātā ar statusu `optimal` ir `total_profit`, `items` ar laukiem `order_id`, `quantity`, `profit`, kā arī `machines` ar laukiem `machine_id`, `available_time`, `printing_time`, `maintenance_count`, `maintenance_time`, `used_time`, `remaining_time`, `effective_printing_time` un `utilization_percent`. Tirāžas un apkopju skaitu atgriež kā veselus skaitļus. Rezultātu var tieši serializēt JSON.

## 8. Aprēķina piemērs

| Pasūtījums | Peļņa par vienību | Minimālā tirāža | Printer (min/gab.) | Cutter (min/gab.) |
|---|---:|---:|---:|---:|
| A | 6 | 2 | 1 | 1 |
| B | 10 | 1 | 2 | 1 |

| Iekārta | $T$ | $W$ | $M$ | $T^{\mathrm{eff}}$ | Drukāšana | Apkopju skaits | Apkopes laiks | Izmantots | Atlikums | Noslodze |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Printer | 10 | 4 | 1 | 8 | 8 | 1 | 1 | 9 | 1 | 90% |
| Cutter | 9 | 3 | 1 | 7 | 7 | 2 | 2 | 9 | 0 | 100% |

Optimālās tirāžas ir A = 6 un B = 1. Kopējā peļņa ir $6\cdot6 + 10\cdot1 = 46$.

## 9. Kļūdu apstrāde

| Statuss | Nosacījums |
|---|---|
| `optimal` | CBC ir pierādījis optimalitāti, un plāns izturējis pārbaudes. |
| `invalid_input` | Tukši vai nepilnīgi dati, nepareizs tips, dublikāts, nederīga atsauce vai vērtība. |
| `infeasible` | Iekārtu jauda nav pietiekama obligātajiem tirāžiem. |
| `unbounded` | Ir pelnošs pasūtījums, kam visu iekārtu laiki ir nulle, un obligātos tirāžus var izpildīt. |
| `solver_error` | CBC nav pieejams, izpilde beidzas ar kļūdu vai rezultāts neatbilst modeļa pārbaudēm. |
| `not_solved` | CBC nav pierādījis risinājuma optimalitāti. |

Neveiksmes gadījumā atbilde satur tikai `status` un `message`. HTTP statusi aprakstīti [API līgumā](API_CONTRACT.md#optimization).

## 10. Modeļa pieņēmumi un ierobežojumi

- Perioda sākumā iekārtas ir gatavas darbam. Drukāšanu var pārtraukt, lai veiktu apkopi.
- Modelis apkopo resursu patēriņu visā periodā. Pasūtījumu secība, operāciju grafiks un pārejas starp iekārtām paliek ārpus modeļa.
- Ja vairākiem plāniem ir vienāda peļņa, CBC var izvēlēties jebkuru no tiem. Pasūtījumam ar nulles peļņu un nulles resursu patēriņu modulis izvēlas minimālo tirāžu.
- CBC izmanto peldošā komata aritmētiku. Ievades mērogs un koeficientu attiecības var ietekmēt risinātāja skaitlisko precizitāti.
- Esošam PostgreSQL sējumam jābūt piemērotai migrācijai `machinesmaintain.sql`. Ja pēc migrācijas iepriekšējā API versija datubāzē ierakstīja stundas, skartie ieraksti jāidentificē un jāpārbauda pirms plānošanas.
- Ja iekārtai vēl nav konfigurēts `continuousPrintingTime`, aprēķins atgriež `invalid_input`. To var iestatīt ar iekārtu API. Pašreizējā tīmekļa forma šo parametru nepiedāvā.

## 11. Optimizācijas moduļa izmantošana un testēšana

Servera puses kods ar sagatavotiem datiem var izsaukt moduli tieši.

```python
from backend.optimizer import optimize

plan = optimize(
    orders=[{"id": 1, "book_id": 2, "profit_per_unit": 6, "min_quantity": 2}],
    machines=[{
        "id": 3,
        "available_time": 10,
        "continuous_printing_time": 4,
        "maintenance_time": 1,
    }],
    processing_times=[{"book_id": 2, "machine_id": 3, "time": 1}],
)
```

Piemērā iegūst tirāžu 8, peļņu 48, vienu apkopi un vienu atlikušo minūti. Lietotne izsauc to pašu funkciju ar `POST /api/optimize`, izmantojot konsekventu PostgreSQL datu momentuzņēmumu. Lai pārbaudītu moduli un Flask atbildes formātu, projekta saknē izpilda šīs komandas.

```bash
python -m pip install -r backend/requirements.txt pytest
python -m pytest -q backend/tests
```

Testi ietver kontrolpiemēru, projekta R1 un R2 references gadījumus, pilnu mazu uzdevumu pārlasi, apkopes robežgadījumus un Flask maršrutu ar aizvietotu datubāzes savienojumu.
