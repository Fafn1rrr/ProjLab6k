# Tehnoloģiju steks

## Servera puse

| Slānis | Tehnoloģija | Pamatojums |
|---|---|---|
| Satvars | Flask | Flask tika apskatīts lekcijā, un mums jau ir pieredze darbā ar šo ietvaru. Tas ir vienkāršs un piemērots mūsu risinājuma izstrādei. |
| Programmēšanas valoda | Python | Python jau ir pazīstama programmēšanas valoda un ir ērti izmantojama gan tīmekļa lietotnes loģikai, gan optimizācijas uzdevumu risināšanai. |
| Optimizācijas risinājums | PuLP + CBC Solver | Tiek izmantots veselo skaitļu lineārās programmēšanas (ILP) modeļa izveidei un optimāla drukāšanas plāna aprēķināšanai, maksimizējot peļņu un ievērojot iekārtu darbības laika ierobežojumus. Veseli skaitļi ir nepieciešami, jo grāmatas drukā veselos eksemplāros. CBC izmanto zaru un robežu metodi (branch and bound) un atrod pierādāmi optimālu risinājumu. |
| Datu bāze | PostgreSQL | Relāciju datu bāze, kas ir piemērota grāmatu, pasūtījumu, iekārtu un drukāšanas plānu datu glabāšanai. |
| Tīmekļa serveris | Gunicorn | Gunicorn ir vienkāršs veids, kā darbināt Flask lietotni servera vidē, un tas labi darbojas kopā ar Python un Linux. |
| OS | Ubuntu | Bezmaksas un plaši izmantota Linux operētājsistēma. |
| Serveris | IaaS | Jo Microsoft Azure studentiem piedāvā iespēju noteiktu laiku bez maksas izmantot serveri projekta vajadzībām. Tas mums arī dos praktisku pieredzi sistēmas izvietošanā jeb deployment procesā. |

## Klienta puse

| Slānis | Tehnoloģija | Pamatojums |
|---|---|---|
| Struktūra un stils | HTML5 + CSS3 | HTML tiks izmantots tīmekļa lapu struktūras izveidei, bet CSS – lietotāja saskarnes noformēšanai. |
| Programmēšanas valoda | JavaScript | Tiks izmantots interaktīvām darbībām lietotāja saskarnē, lai nebūtu nepieciešams katru darbību apstrādāt tikai servera pusē. |
| Lietotāja saskarnes bibliotēka | Bootstrap 5 | Ļauj ātrāk izveidot pārskatāmu un pielāgojamu saskarni, izmantojot jau gatavus elementus, piemēram, pogas, formas un tabulas. |