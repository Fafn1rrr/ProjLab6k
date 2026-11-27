# Prasību formulējums

## 1. Sistēmas funkcijas un iezīmes

| Nr. | Prasība | Prioritāte |
|---|---|---|
| F1 | Sistēmai jānodrošina grāmatu pasūtījumu pievienošana, katram pasūtījumam norādot vienu grāmatu. | Must have |
| F2 | Sistēmai jānodrošina iespēja norādīt katras grāmatas peļņu par vienību. | Must have |
| F3 | Sistēmai jānodrošina iespēja norādīt minimālo drukājamo grāmatu skaitu katram pasūtījumam. (šis daudzums obligāti jāizdrukā). | Must have |
| F4 | Sistēmai jānodrošina pieejamo drukāšanas iekārtu norādīšana. | Must have |
| F5 | Sistēmai jānodrošina iespēja norādīt katras iekārtas kopējo pieejamo laiku plānošanas periodā, ieskaitot drukāšanas un apkopes laiku. | Must have |
| F6 | Sistēmai jānodrošina iespēja norādīt katrai grāmatai nepieciešamo iekārtas darbības laiku. | Must have |
| F7 | Sistēmai jāaprēķina optimāls drukāšanas plāns, maksimizējot peļņu un ievērojot pasūtījumu minimālos daudzumus, iekārtu kopējā pieejamā laika ierobežojumus un obligātās apkopes pārtraukumus. | Must have |
| F8 | Sistēmai jāattēlo, kuras grāmatas un kādā daudzumā ir jādrukā. | Must have |
| F9 | Sistēmai jāattēlo aprēķinātā kopējā peļņa. | Must have |
| F10 | Sistēmai jāattēlo katras iekārtas drukāšanai izmantotais laiks, apkopes laiks un atlikušais pieejamais laiks. | Should have |
| F11 | Sistēmai jānodrošina iepriekš ievadīto grāmatu un iekārtu datu rediģēšana. | Should have |
| F12 | Sistēmai jānodrošina iepriekš aprēķināto drukāšanas plānu saglabāšana un apskate. | Could have |
| F13 | Sistēmai jānodrošina iespēja katrai iekārtai norādīt maksimālo nepārtrauktas drukāšanas laiku līdz obligātajai apkopei un apkopes ilgumu. | Must have |

## 2. Lietotāju stāsti

Galvenais sistēmas lietotājs ir **ražošanas plānotājs**.

Lietotāju stāsti tiek formulēti pēc principa:

**<lietotājs> vēlas <sasniegt mērķi>, jo <ieguvums>.**

| Nr. | Lietotāju stāsts | Prioritāte |
|---|---|---|
| US1 | Ražošanas plānotājs vēlas pievienot grāmatu pasūtījumus, jo tie ir nepieciešami drukāšanas plāna izveidošanai. | Must have |
| US2 | Ražošanas plānotājs vēlas norādīt katras grāmatas peļņu par vienību, jo sistēmai ir jāspēj maksimizēt kopējo peļņu. | Must have |
| US3 | Ražošanas plānotājs vēlas norādīt minimālo drukājamo grāmatu skaitu, jo drukāšanas plānam ir jāievēro pasūtījumu ierobežojumi. | Must have |
| US4 | Ražošanas plānotājs vēlas norādīt pieejamās drukāšanas iekārtas, jo drukāšanas plānam ir jāņem vērā pieejamās iekārtas. | Must have |
| US5 | Ražošanas plānotājs vēlas norādīt katras iekārtas kopējo pieejamo laiku, jo plānošanā jāņem vērā gan drukāšana, gan apkopes pārtraukumi. | Must have |
| US6 | Ražošanas plānotājs vēlas norādīt katrai grāmatai nepieciešamo iekārtas darbības laiku, jo sistēmai ir jāņem vērā iekārtu noslodze. | Must have |
| US7 | Ražošanas plānotājs vēlas iegūt optimālu drukāšanas plānu, jo nepieciešams maksimizēt peļņu, ievērojot pasūtījumu minimālos daudzumus, iekārtu pieejamo laiku un apkopes pārtraukumus. | Must have |
| US8 | Ražošanas plānotājs vēlas redzēt, kuras grāmatas un kādā daudzumā ir jādrukā, jo nepieciešams zināt, kurus pasūtījumus ir izdevīgi ražot. | Must have |
| US9 | Ražošanas plānotājs vēlas redzēt aprēķināto kopējo peļņu, jo nepieciešams novērtēt izveidotā drukāšanas plāna rezultātu. | Must have |
| US10 | Ražošanas plānotājs vēlas redzēt katras iekārtas drukāšanas laiku, apkopes laiku un atlikušo pieejamo laiku, jo nepieciešams novērtēt iekārtu noslodzi. | Should have |
| US11 | Ražošanas plānotājs vēlas rediģēt iepriekš ievadītos grāmatu un iekārtu datus, jo sākotnējā informācija var mainīties. | Should have |
| US12 | Ražošanas plānotājs vēlas saglabāt un apskatīt iepriekš aprēķinātos drukāšanas plānus, jo tos var būt nepieciešams izmantot vēlāk. | Could have |
| US13 | Ražošanas plānotājs vēlas norādīt katras iekārtas nepārtrauktas drukāšanas laiku līdz obligātajai apkopei un apkopes ilgumu, jo drukāšanas plānā jāņem vērā apkopes radītie pārtraukumi. | Must have |

**Piemērs:** ja iekārta ir pieejama 12 stundas, var drukāt 4 stundas bez pārtraukuma un apkopes ilgums ir 1 stunda, iespējamais sadalījums ir **4 h drukāšana + 1 h apkope + 4 h drukāšana + 1 h apkope + 2 h drukāšana**. Kopā: **10 stundas drukāšanai**, **2 stundas apkopei**.
